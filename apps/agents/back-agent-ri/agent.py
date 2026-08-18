from typing import Any


def run(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": request.get("ticker"),
        "documents": [],
        "summary": "RI document retrieval tool ready for ingestion and RAG integration.",
    }
