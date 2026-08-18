import os
import json
from uuid import uuid4

from mcp import ClientSession
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from gateway.guardrails import guard_input, guard_output
from gateway.memory import memory

app = FastAPI(title="Data Master Agent Gateway", version="0.1.0")

MCP_URL = os.getenv("MCP_URL", "http://localhost:8101/mcp")
MCP_SERVICE_TOKEN = os.getenv("MCP_SERVICE_TOKEN")


class GatewayRequest(BaseModel):
    trace_id: str | None = None
    client_id: str = Field(min_length=1, max_length=100)
    session_id: str | None = Field(default=None, min_length=16, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
    message: str = Field(min_length=1, max_length=2000)
    intent: str | None = Field(default=None, pattern="^(portfolio|market|news|ri|web)$")
    ticker: str | None = Field(default=None, pattern=r"^[A-Z]{4}[0-9]{1,2}\.SA$")
    parameters: dict = Field(default_factory=dict)


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway", "mcp_url": MCP_URL}


@app.post("/v1/agent/run")
async def run_agent(request: GatewayRequest):
    allowed, reason = guard_input(request.message)
    if not allowed:
        raise HTTPException(status_code=400, detail=reason)

    trace_id = request.trace_id or str(uuid4())
    session_id = request.session_id or str(uuid4())
    if not MCP_SERVICE_TOKEN:
        raise HTTPException(status_code=503, detail="MCP service authorization is not configured")
    payload = request.model_dump(exclude_none=True)
    payload["trace_id"] = trace_id
    payload["session_id"] = session_id
    payload["history"] = memory.history(request.client_id, session_id)
    memory.append(request.client_id, session_id, "user", request.message)
    try:
        async with create_mcp_http_client(
            headers={"Authorization": f"Bearer {MCP_SERVICE_TOKEN}"}
        ) as http_client:
            async with streamable_http_client(MCP_URL, http_client=http_client) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    if not any(tool.name == "build_context" for tool in tools.tools):
                        raise HTTPException(status_code=502, detail="MCP build_context tool unavailable")
                    result = await session.call_tool(
                        "build_context",
                        {"request_json": json.dumps(payload, ensure_ascii=False)},
                    )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Unified MCP protocol unavailable") from exc

    if not result.content or not hasattr(result.content[0], "text"):
        raise HTTPException(status_code=502, detail="MCP returned an empty tool result")
    try:
        context = json.loads(result.content[0].text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="MCP returned invalid JSON context") from exc
    allowed, reason = guard_output(context)
    if not allowed:
        raise HTTPException(status_code=502, detail=reason)
    memory.append(request.client_id, session_id, "assistant", context.get("answer", ""))
    return {"trace_id": trace_id, "client_id": request.client_id, "session_id": session_id, "status": "ok", "context": context}
