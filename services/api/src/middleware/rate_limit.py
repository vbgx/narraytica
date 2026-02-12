from __future__ import annotations

import time
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_epoch: int
    retry_after: int


def _now() -> float:
    return time.time()


def _window_reset_epoch(now: float, window_seconds: int) -> int:
    return int(now // window_seconds) * window_seconds + window_seconds


def _extract_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _extract_api_key(request: Request) -> str | None:
    x = request.headers.get("x-api-key")
    if x and x.strip():
        return x.strip()

    auth = request.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        tok = auth[7:].strip()
        return tok or None

    return None


class InMemoryStore:
    def __init__(self) -> None:
        self._buckets: dict[str, tuple[int, int]] = {}

    def incr(self, key: str, window_seconds: int) -> tuple[int, int]:
        now = _now()
        reset = _window_reset_epoch(now, window_seconds)
        cur = self._buckets.get(key)

        if not cur or cur[0] != reset:
            self._buckets[key] = (reset, 1)
            return reset, 1

        self._buckets[key] = (reset, cur[1] + 1)
        return reset, cur[1] + 1


class RedisStore:
    def __init__(self, url: str) -> None:
        if redis is None:
            raise RuntimeError("redis package not installed")
        self._r = redis.Redis.from_url(url, decode_responses=True)

    def incr(self, key: str, window_seconds: int) -> tuple[int, int]:
        now = _now()
        reset = _window_reset_epoch(now, window_seconds)
        redis_key = f"rl:{reset}:{key}"

        pipe = self._r.pipeline()
        pipe.incr(redis_key, 1)
        pipe.expireat(redis_key, reset)
        out = pipe.execute()

        count = int(out[0])
        return reset, count


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        enabled: bool,
        limit: int,
        window_seconds: int,
        redis_url: str | None = None,
        path_prefix: str = "/api/",
    ) -> None:
        super().__init__(app)
        self.enabled = bool(enabled)
        self.limit = int(limit)
        self.window_seconds = int(window_seconds)
        self.path_prefix = path_prefix.rstrip("/") + "/"

        # Prefer Redis if configured AND redis package is available.
        # Otherwise fall back to in-memory (dev/tests).
        self._store = InMemoryStore()
        if redis_url and redis is not None:
            try:
                self._store = RedisStore(redis_url)
            except Exception:
                # Fail open to in-memory rather than crashing app/tests
                self._store = InMemoryStore()

    def _should_apply(self, request: Request) -> bool:
        if not self.enabled:
            return False
        return request.url.path.startswith(self.path_prefix)

    def _bucket_key(self, request: Request) -> str:
        api_key = _extract_api_key(request)
        if api_key:
            return f"key:{api_key}"
        return f"ip:{_extract_client_ip(request)}"

    def _check(self, request: Request) -> RateLimitResult:
        key = self._bucket_key(request)
        reset, count = self._store.incr(key, self.window_seconds)

        remaining = max(0, self.limit - count)
        allowed = count <= self.limit
        retry_after = max(0, int(reset - _now()))

        return RateLimitResult(
            allowed=allowed,
            limit=self.limit,
            remaining=remaining if allowed else 0,
            reset_epoch=int(reset),
            retry_after=retry_after,
        )

    @staticmethod
    def _apply_headers(resp: Response, rl: RateLimitResult) -> None:
        resp.headers["X-RateLimit-Limit"] = str(rl.limit)
        resp.headers["X-RateLimit-Remaining"] = str(rl.remaining)
        resp.headers["X-RateLimit-Reset"] = str(rl.reset_epoch)
        if not rl.allowed:
            resp.headers["Retry-After"] = str(rl.retry_after)

    async def dispatch(self, request: Request, call_next):
        if not self._should_apply(request):
            return await call_next(request)

        rl = self._check(request)
        if not rl.allowed:
            resp = Response(status_code=429, content="Too Many Requests")
            self._apply_headers(resp, rl)
            return resp

        resp = await call_next(request)
        self._apply_headers(resp, rl)
        return resp
