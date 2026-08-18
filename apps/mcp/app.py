"""Unified MCP with a bounded ReAct-style tool loop."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = ROOT / "agents"


class MCPRequest(BaseModel):
    trace_id: str
    client_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)
    intent: str | None = Field(default=None, pattern="^(portfolio|market|news|ri|web)$")
    ticker: str | None = Field(default=None, pattern=r"^[A-Z]{4}[0-9]{1,2}\.SA$")
    parameters: dict[str, Any] = Field(default_factory=dict)


class MCPContext(BaseModel):
    trace_id: str
    status: str
    answer: str
    tools_called: list[str]
    observations: list[dict[str, Any]]
    sources: list[str] = Field(default_factory=list)


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
    selected_tools = reason(request.message, request.intent)
    observations: list[dict[str, Any]] = []
    sources: list[str] = []
    for tool_name in selected_tools[:3]:
        payload = request.model_dump()
        payload["parameters"] = {**request.parameters, "reason": request.message}
        observation = TOOLS[tool_name](payload)
        observations.append({"tool": tool_name, "result": observation})
        sources.extend(observation.get("sources", []))
    answer = "Contexto consolidado pelas ferramentas: " + ", ".join(selected_tools[:3])
    return MCPContext(
        trace_id=request.trace_id,
        status="ok",
        answer=answer,
        tools_called=selected_tools[:3],
        observations=observations,
        sources=list(dict.fromkeys(sources)),
    )


app = FastAPI(title="Data Master Unified MCP", version="0.2.0")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "mcp", "tools": list(TOOLS)}


@app.post("/v1/context", response_model=MCPContext)
def build_context(request: MCPRequest) -> MCPContext:
    return execute(request)
