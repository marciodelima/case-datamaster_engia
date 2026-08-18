from __future__ import annotations

import os
from typing import Any

import requests


class GatewayClient:
    def __init__(self, base_url: str | None = None, token: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("GATEWAY_URL", "http://localhost:8100")).rstrip("/")
        self.token = token or os.getenv("GATEWAY_JWT_TOKEN")

    def ask(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.token:
            raise RuntimeError("GATEWAY_JWT_TOKEN is not configured")
        response = requests.post(
            f"{self.base_url}/v1/agent/run",
            json=payload,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
