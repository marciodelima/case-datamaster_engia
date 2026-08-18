from typing import Any


def run(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "query": request.get("parameters", {}).get("query"),
        "results": [],
        "summary": "Web research tool ready for an allowlisted search provider.",
    }
