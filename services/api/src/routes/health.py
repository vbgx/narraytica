from __future__ import annotations

import socket
from typing import Any

from fastapi import APIRouter, Response, status

from ..config import settings
from ..wiring.health import check_postgres

router = APIRouter(prefix="/health", tags=["health"])


def _redis_ping(redis_url: str, timeout_s: float = 1.0) -> tuple[bool, str]:
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


@router.get("")
def health(resp: Response) -> dict[str, Any]:
    out: dict[str, Any] = {"status": "ok"}

    try:
        if settings.api_database_url:
            out["db"] = "ok" if check_postgres() else "error"
            if out["db"] != "ok":
                out["status"] = "degraded"
                resp.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            out["db"] = "skipped"
    except Exception as e:
        out["db"] = "error"
        out["db_error"] = str(e)
        out["status"] = "degraded"
        resp.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    if settings.redis_url:
        ok, msg = _redis_ping(settings.redis_url)
        out["redis"] = "ok" if ok else "error"
        if not ok:
            out["redis_error"] = msg
            out["status"] = "degraded"
            resp.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return out
