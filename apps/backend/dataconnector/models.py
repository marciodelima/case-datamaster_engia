from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolRequest(BaseModel):
    trace_id: str | None = None
    client_id: str = Field(min_length=1, max_length=100)
    ticker: str | None = Field(default=None, pattern=r"^[A-Z]{4}[0-9]{1,2}\.SA$")
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolResponse(BaseModel):
    trace_id: str | None = None
    tool: str
    status: Literal["ok", "error"]
    data: dict[str, Any] = Field(default_factory=dict)
    sources: list[str] = Field(default_factory=list)


class GatewayRequest(BaseModel):
    trace_id: str | None = None
    client_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)
    intent: Literal["portfolio", "market", "news", "ri", "web"] | None = None
    ticker: str | None = Field(default=None, pattern=r"^[A-Z]{4}[0-9]{1,2}\.SA$")
    parameters: dict[str, Any] = Field(default_factory=dict)


class BackendHealth(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    version: str = "0.1.0"
