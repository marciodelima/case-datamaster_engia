from typing import Any


def run(request: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic portfolio facts; no LLM is used for calculations."""
    return {
        "client_id": request["client_id"],
        "ticker": request.get("ticker"),
        "summary": "Portfolio tool ready for holdings, exposure and risk calculations.",
        "parameters": request.get("parameters", {}),
    }
