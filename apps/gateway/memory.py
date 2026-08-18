"""Bounded, process-local short-term chat memory scoped by client and session."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any


class ScopedMemory:
    def __init__(self, max_messages: int = 20, ttl_minutes: int = 120) -> None:
        self.max_messages = max_messages
        self.ttl = timedelta(minutes=ttl_minutes)
        self._items: dict[tuple[str, str], deque[dict[str, Any]]] = defaultdict(
            lambda: deque(maxlen=self.max_messages)
        )
        self._updated: dict[tuple[str, str], datetime] = {}
        self._lock = Lock()

    def _key(self, client_id: str, session_id: str) -> tuple[str, str]:
        return client_id, session_id

    def history(self, client_id: str, session_id: str) -> list[dict[str, Any]]:
        with self._lock:
            key = self._key(client_id, session_id)
            if datetime.now(timezone.utc) - self._updated.get(key, datetime.min.replace(tzinfo=timezone.utc)) > self.ttl:
                self._items.pop(key, None)
                self._updated.pop(key, None)
                return []
            return list(self._items.get(key, []))

    def append(self, client_id: str, session_id: str, role: str, content: str) -> None:
        with self._lock:
            key = self._key(client_id, session_id)
            self._items[key].append({"role": role, "content": content[:4000]})
            self._updated[key] = datetime.now(timezone.utc)


memory = ScopedMemory()
