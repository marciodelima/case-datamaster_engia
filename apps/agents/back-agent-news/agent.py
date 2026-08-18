from typing import Any


def run(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": request.get("ticker"),
        "items": [],
        "summary": "News search tool ready; connect an approved provider before production use.",
    }
