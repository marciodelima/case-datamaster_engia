import os
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from gateway.guardrails import guard_input, guard_output

app = FastAPI(title="Data Master Agent Gateway", version="0.1.0")

MCP_URL = os.getenv("MCP_URL", "http://localhost:8101/v1/context")


class GatewayRequest(BaseModel):
    trace_id: str | None = None
    client_id: str = Field(min_length=1, max_length=100)
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
    payload = request.model_dump(exclude_none=True)
    payload["trace_id"] = trace_id
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(MCP_URL, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Unified MCP unavailable") from exc

    context = response.json()
    allowed, reason = guard_output(context)
    if not allowed:
        raise HTTPException(status_code=502, detail=reason)
    return {"trace_id": trace_id, "status": "ok", "context": context}
