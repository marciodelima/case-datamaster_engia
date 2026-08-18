"""Redis-backed short-term chat memory scoped by client."""

from __future__ import annotations

import json
import os
from typing import Any

from redis.asyncio import Redis


class ScopedMemory:
    def __init__(self, max_messages: int = 20, ttl_minutes: int = 120) -> None:
        self.max_messages = max_messages
        self.ttl_seconds = ttl_minutes * 60
        self.redis: Redis = Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True,
        )

    def _key(self, client_id: str) -> str:
        return f"datamaster:chat:client:{client_id}"

    async def history(self, client_id: str) -> list[dict[str, Any]]:
        values = await self.redis.lrange(self._key(client_id), 0, self.max_messages - 1)
        return [json.loads(value) for value in values]

    async def append(self, client_id: str, role: str, content: str) -> None:
        key = self._key(client_id)
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.rpush(key, json.dumps({"role": role, "content": content[:4000]}, ensure_ascii=False))
            await pipe.ltrim(key, -self.max_messages, -1)
            await pipe.expire(key, self.ttl_seconds)
            await pipe.execute()

    async def ping(self) -> bool:
        return bool(await self.redis.ping())


memory = ScopedMemory()
