from __future__ import annotations

import socket
import time
from typing import Any

import psycopg
from fastapi import APIRouter, Response, status
from settings import settings

router = APIRouter(prefix="/health", tags=["health"])


def _redis_ping(redis_url: str, timeout_s: float = 1.0) -> tuple[bool, str]:
    """
    Minimal Redis PING without external deps.

    Expects: redis://host:port[/db]
    """
    try:
        if not redis_url.startswith("redis://"):
            return False, "invalid_scheme"

        rest = redis_url[len("redis://") :]
        hostport = rest.split("/", 1)[0]

        if ":" in hostport:
            host, port_str = hostport.split(":", 1)
            port = int(port_str)
        else:
            host, port = hostport, 6379

        with socket.create_connection((host, port), timeout=timeout_s) as sock:
            sock.settimeout(timeout_s)
            sock.sendall(b"*1\r\n$4\r\nPING\r\n")
            data = sock.recv(64)

        if data.startswith(b"+PONG"):
            return True, "ok"

        return False, f"unexpected_reply:{data[:32]!r}"
    except Exception as e:
        return False, str(e)


def _db_ping(database_url: str, timeout_s: float = 1.0) -> tuple[bool, str]:
    """
    Real DB check (auth + SELECT 1) using psycopg (already in stack via
    SQLAlchemy / Alembic).

    Accepts SQLAlchemy-style DSN: postgresql+psycopg://...
    """
    try:
        dsn = database_url.replace("postgresql+psycopg://", "postgresql://")
        with psycopg.connect(dsn, connect_timeout=timeout_s) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()

        return True, "ok"
    except Exception as e:
        return False, str(e)


@router.get("", summary="Legacy health endpoint")
def health() -> dict[str, Any]:
    # Compatibility: GET /health -> {"status":"ok"}
    return {"status": "ok"}


@router.get("/live", summary="Liveness probe (process up)")
def health_live() -> dict[str, Any]:
    return {"status": "ok", "probe": "live"}


@router.get("/ready", summary="Readiness probe (deps available)")
def health_ready(response: Response) -> dict[str, Any]:
    started = time.perf_counter()

    db_ok, db_msg = _db_ping(settings.database_url, timeout_s=1.0)
    redis_ok, redis_msg = _redis_ping(settings.redis_url, timeout_s=1.0)

    checks: dict[str, dict[str, Any]] = {
        "postgres": {"ok": db_ok, "detail": db_msg},
        "redis": {"ok": redis_ok, "detail": redis_msg},
    }

    ok = all(v["ok"] for v in checks.values())
    duration_ms = int((time.perf_counter() - started) * 1000)

    payload: dict[str, Any] = {
        "status": "ok" if ok else "fail",
        "probe": "ready",
        "duration_ms": duration_ms,
        "checks": checks,
    }

    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return payload
