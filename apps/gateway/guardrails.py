from __future__ import annotations

import re
from typing import Any

BLOCKED_PATTERNS = re.compile(
    r"(ignore\s+(all|previous|prior)\s+instructions|system\s+prompt|jailbreak|developer\s+message|reveal\s+(secrets|keys|tokens))",
    re.IGNORECASE,
)


def guard_input(message: str) -> tuple[bool, str | None]:
    if len(message.strip()) < 2:
        return False, "Message must contain at least two characters."
    if BLOCKED_PATTERNS.search(message):
        return False, "Request blocked by input safety policy."
    return True, None


def guard_output(context: dict[str, Any]) -> tuple[bool, str | None]:
    if context.get("status") != "ok":
        return False, "MCP returned an invalid status."
    if not context.get("answer") or not isinstance(context.get("observations"), list):
        return False, "MCP context failed output validation."
    return True, None
