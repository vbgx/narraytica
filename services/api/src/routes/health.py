from __future__ import annotations

import socket
import time
from typing import Any, Dict, Tuple

import psycopg
from fastapi import APIRouter, Response, status

from settings import settings

router = APIRouter(prefix="/health", tags=["health"])


def _redis_ping(redis_url: str, timeout_s: float = 1.0) -> Tuple[bool, str]:
    """
    Minimal Redis PING without external deps.
    Expects a classic URL: redis://host:port[/db]
    """
    try:
        # very small URL parsing (no dependency)
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


def _db_ping(database_url: str, timeout_s: float = 1.0) -> Tuple[bool, str]:
    """
    Real DB check (auth + SELECT 1), using psycopg (already in stack via SQLAlchemy/Alembic).
    Accepts SQLAlchemy style: postgresql+psycopg://...
    """
    try:
        dsn = database_url.replace("postgresql+psycopg://", "postgresql://")
        with psycopg.connect(dsn, connect_timeout=timeout_s) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                _ = cur.fetchone()
        return True, "ok"
    except Exception as e:
        return False, str(e)


@router.get("", summary="Legacy health endpoint")
def health() -> Dict[str, Any]:
    # Keep compatibility with your current test: curl .../health -> {"status":"ok"}
    return {"status": "ok"}


@router.get("/live", summary="Liveness probe (process up)")
def health_live() -> Dict[str, Any]:
    # Should never fail unless process is dead.
    return {"status": "ok", "probe": "live"}


@router.get("/ready", summary="Readiness probe (deps available)")
def health_ready(response: Response) -> Dict[str, Any]:
    started = time.perf_counter()

    checks: Dict[str, Dict[str, Any]] = {}

    db_ok, db_msg = _db_ping(settings.database_url, timeout_s=1.0)
    checks["postgres"] = {"ok": db_ok, "detail": db_msg}

    redis_ok, redis_msg = _redis_ping(settings.redis_url, timeout_s=1.0)
    checks["redis"] = {"ok": redis_ok, "detail": redis_msg}

    ok = all(x["ok"] for x in checks.values())
    duration_ms = int((time.perf_counter() - started) * 1000)

    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "fail",
            "probe": "ready",
            "duration_ms": duration_ms,
            "checks": checks,
        }

    return {
        "status": "ok",
        "probe": "ready",
        "duration_ms": duration_ms,
        "checks": checks,
    }
