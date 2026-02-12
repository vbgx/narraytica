from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Protocol


class IdempotencyStore(Protocol):
    def get(self, key: str) -> dict[str, Any] | None: ...
    def set(self, key: str, value: dict[str, Any], ttl_seconds: int = 3600) -> None: ...


# -----------------------------------------------------------------------------
# In-memory fallback (dev/tests)
# -----------------------------------------------------------------------------
@dataclass
class MemoryIdempotencyStore:
    _data: dict[str, tuple[float, dict[str, Any]]]

    def __init__(self) -> None:
        self._data = {}

    def get(self, key: str) -> dict[str, Any] | None:
        item = self._data.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < time.time():
            self._data.pop(key, None)
            return None
        return value

    def set(self, key: str, value: dict[str, Any], ttl_seconds: int = 3600) -> None:
        self._data[key] = (time.time() + ttl_seconds, value)


# -----------------------------------------------------------------------------
# Redis store (optional)
# -----------------------------------------------------------------------------
@dataclass
class RedisIdempotencyStore:
    redis_url: str

    def _client(self):
        import redis  # type: ignore

        return redis.Redis.from_url(self.redis_url, decode_responses=True)

    def get(self, key: str) -> dict[str, Any] | None:
        r = self._client()
        raw = r.get(key)
        if not raw:
            return None
        return json.loads(raw)

    def set(self, key: str, value: dict[str, Any], ttl_seconds: int = 3600) -> None:
        r = self._client()
        r.setex(key, ttl_seconds, json.dumps(value))


_memory_singleton = MemoryIdempotencyStore()


def _redis_available() -> bool:
    try:
        import redis  # noqa: F401
    except Exception:
        return False
    return True


def get_idempotency_store() -> IdempotencyStore:
    """
    If REDIS_URL is set AND redis client is installed, use Redis.
    Otherwise, fall back to in-memory (tests/local dev).
    """
    url = os.environ.get("REDIS_URL")
    if url and _redis_available():
        return RedisIdempotencyStore(url)
    return _memory_singleton
