from typing import Any


def run(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": request.get("ticker"),
        "period": request.get("parameters", {}).get("period", "6mo"),
        "prices": [],
        "summary": "Market-price tool ready for a provider adapter.",
    }
