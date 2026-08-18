"""Unified MCP with a bounded ReAct-style tool loop."""

from __future__ import annotations

import importlib.util
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Callable

import json

from mcp.server.mcpserver import MCPServer
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

try:
    from service.memory import memory
except ModuleNotFoundError:
    from memory import memory

try:
    from service.llm import judge_model_name, judge_response, model_name, plan_tools, synthesize
except ModuleNotFoundError:
    from llm import judge_model_name, judge_response, model_name, plan_tools, synthesize

ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = ROOT / "agents"


class MCPRequest(BaseModel):
    trace_id: str
    client_id: str = Field(min_length=1, max_length=100)
    session_id: str = Field(min_length=16, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
    history: list[dict[str, str]] = Field(default_factory=list, max_length=20)
    message: str = Field(min_length=1, max_length=2000)
    intent: str | None = Field(default=None, pattern="^(portfolio|market|news|ri|web)$")
    ticker: str | None = Field(default=None, pattern=r"^[A-Z]{4}[0-9]{1,2}\.SA$")
    parameters: dict[str, Any] = Field(default_factory=dict)


class MCPContext(BaseModel):
    trace_id: str
    client_id: str
    session_id: str
    status: str
    answer: str
    planner: str
    plan: list[str]
    tools_called: list[str]
    observations: list[dict[str, Any]]
    sources: list[str] = Field(default_factory=list)
    judge: dict[str, Any] = Field(default_factory=dict)


TOOL_PATHS = {
    "portfolio": AGENTS_ROOT / "back-agent-finance" / "agent.py",
    "market": AGENTS_ROOT / "back-agent-price" / "agent.py",
    "news": AGENTS_ROOT / "back-agent-news" / "agent.py",
    "ri": AGENTS_ROOT / "back-agent-ri" / "agent.py",
    "web": AGENTS_ROOT / "back-agent-web" / "agent.py",
}


def load_tool(name: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    path = TOOL_PATHS[name]
    spec = importlib.util.spec_from_file_location(f"agent_{name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load tool: {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run


TOOLS = {name: load_tool(name) for name in TOOL_PATHS}


def reason(message: str, explicit_intent: str | None) -> list[str]:
    """Select tools using a bounded, deterministic ReAct-style reasoner."""
    if explicit_intent:
        return [explicit_intent]
    text = message.casefold()
    selected: list[str] = []
    rules = {
        "portfolio": ("carteira", "posição", "posições", "risco", "exposição"),
        "market": ("preço", "cotação", "gráfico", "macd", "bollinger", "indicador"),
        "news": ("notícia", "notícias", "mercado", "sentimento"),
        "ri": ("ri", "relatório", "resultado", "balanço", "fato relevante"),
        "web": ("pesquisar", "buscar na internet", "web", "fonte externa"),
    }
    for tool, keywords in rules.items():
        if any(keyword in text for keyword in keywords):
            selected.append(tool)
    return selected or ["portfolio"]


def execute(request: MCPRequest) -> MCPContext:
    history = memory.history(request.client_id, request.session_id)
    memory.append(request.client_id, request.session_id, "user", request.message)
    llm_plan = plan_tools(request.message, request.ticker, request.intent)
    planner = "llm" if llm_plan else "fallback"
    selected_tools = llm_plan or reason(request.message, request.intent)
    selected_tools = [tool for tool in selected_tools if tool in TOOLS][:3]
    if not selected_tools:
        selected_tools = ["portfolio"]

    observations: list[dict[str, Any]] = []
    sources: list[str] = []
    for tool_name in selected_tools:
        payload = request.model_dump()
        payload["parameters"] = {**request.parameters, "reason": request.message}
        try:
            observation = TOOLS[tool_name](payload)
            status = "ok"
        except Exception as exc:
            observation = {"error": "Tool execution failed", "tool": tool_name}
            status = "error"
        observations.append({"tool": tool_name, "result": observation})
        if status == "ok":
            sources.extend(observation.get("sources", []))

    unique_sources = list(dict.fromkeys(sources))
    answer = synthesize(request.message, observations, unique_sources, history)
    if not answer:
        answer = "Contexto consolidado pelas ferramentas: " + ", ".join(selected_tools)
        answer += ". Esse conteúdo não constitui recomendação financeira."
    answer = f"[{model_name()} | planner={planner}] {answer}"
    judge = judge_response(request.message, answer, observations, unique_sources)
    if not judge["approved"]:
        answer = (
            "A resposta foi retida pelo juiz de qualidade por não atingir o nível mínimo de "
            "groundedness, segurança ou clareza. Consulte as observações e fontes disponíveis. "
            "Esse conteúdo não constitui recomendação financeira."
        )
    memory.append(request.client_id, request.session_id, "assistant", answer)
    return MCPContext(
        trace_id=request.trace_id,
        client_id=request.client_id,
        session_id=request.session_id,
        status="ok",
        answer=answer,
        planner=planner,
        plan=selected_tools,
        tools_called=selected_tools,
        observations=observations,
        sources=unique_sources,
        judge=judge,
    )


mcp = MCPServer(
    name="data-master-mcp",
    version="0.3.0",
    description="Financial research MCP for Brazilian equities.",
)


@mcp.tool(
    name="build_context",
    description="Planeja e executa ferramentas financeiras e devolve um contexto fundamentado em JSON.",
    structured_output=False,
)
def build_context(request_json: str) -> str:
    """MCP tool entrypoint; the gateway is the authorized MCP client."""
    request = MCPRequest.model_validate_json(request_json)
    return execute(request).model_dump_json()


app = mcp.streamable_http_app(streamable_http_path="/mcp", json_response=True, host="0.0.0.0")


@asynccontextmanager
async def lifespan(_app):
    async with mcp.session_manager.run():
        yield


app.router.lifespan_context = lifespan


class GatewayOnlyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        expected = os.getenv("MCP_SERVICE_TOKEN")
        received = request.headers.get("authorization", "")
        valid = bool(expected) and secrets.compare_digest(received, f"Bearer {expected}")
        if not valid:
            return JSONResponse({"detail": "MCP access is restricted to the gateway."}, status_code=401)
        return await call_next(request)


app.add_middleware(GatewayOnlyMiddleware)
