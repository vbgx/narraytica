from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from services.api.src.middleware.rate_limit import RateLimitMiddleware


def make_app(*, limit: int = 2, window_seconds: int = 60) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware,
        enabled=True,
        limit=limit,
        window_seconds=window_seconds,
        redis_url=None,  # in-memory for unit tests
        path_prefix="/api/",
    )

    @app.get("/api/ping")
    def ping():
        return {"ok": True}

    @app.get("/public")
    def public():
        return {"ok": True}

    return app


def test_rate_limit_429_and_headers():
    app = make_app(limit=2)
    c = TestClient(app)

    r1 = c.get("/api/ping", headers={"x-api-key": "k1"})
    assert r1.status_code == 200
    assert r1.headers["X-RateLimit-Limit"] == "2"
    assert "X-RateLimit-Remaining" in r1.headers
    assert "X-RateLimit-Reset" in r1.headers

    r2 = c.get("/api/ping", headers={"x-api-key": "k1"})
    assert r2.status_code == 200

    r3 = c.get("/api/ping", headers={"x-api-key": "k1"})
    assert r3.status_code == 429
    assert r3.headers["X-RateLimit-Limit"] == "2"
    assert r3.headers["X-RateLimit-Remaining"] == "0"
    assert "X-RateLimit-Reset" in r3.headers
    assert "Retry-After" in r3.headers


def test_rate_limit_is_per_api_key_bucket():
    app = make_app(limit=1)
    c = TestClient(app)

    r1 = c.get("/api/ping", headers={"x-api-key": "k1"})
    assert r1.status_code == 200

    r2 = c.get("/api/ping", headers={"x-api-key": "k1"})
    assert r2.status_code == 429

    # Different key => different bucket
    r3 = c.get("/api/ping", headers={"x-api-key": "k2"})
    assert r3.status_code == 200


def test_not_applied_outside_prefix():
    app = make_app(limit=1)
    c = TestClient(app)

    for _ in range(5):
        r = c.get("/public")
        assert r.status_code == 200
        assert "X-RateLimit-Limit" not in r.headers
