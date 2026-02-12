from __future__ import annotations

from datetime import UTC, datetime

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, update
from sqlalchemy.engine import Connection

from ..config import settings
from ..db.engine import get_conn
from ..db.schema import api_keys
from .api_keys import hash_api_key
from .errors import forbidden, unauthorized

bearer_scheme = HTTPBearer(auto_error=False)

# Ruff (B008) compliance: avoid calling Depends(...) in function defaults
CREDS_DEP = Depends(bearer_scheme)
CONN_DEP = Depends(get_conn)


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _extract_bearer_token(creds: HTTPAuthorizationCredentials | None) -> str:
    if creds is None:
        raise unauthorized()
    if (creds.scheme or "").lower() != "bearer":
        raise unauthorized("Authorization must use Bearer scheme")
    token = (creds.credentials or "").strip()
    if not token:
        raise unauthorized()
    return token


def require_api_key(
    creds: HTTPAuthorizationCredentials | None = CREDS_DEP,
    conn: Connection = CONN_DEP,
) -> dict:
    token = _extract_bearer_token(creds)

    pepper = settings.api_key_pepper
    if not pepper:
        raise forbidden("API key auth is not configured (missing API_KEY_PEPPER)")

    key_hash = hash_api_key(token, pepper)

    row = (
        conn.execute(select(api_keys).where(api_keys.c.key_hash == key_hash))
        .mappings()
        .first()
    )

    if not row:
        raise forbidden("Invalid or revoked API key")

    if row["status"] != "active":
        raise forbidden("Invalid or revoked API key")

    # best-effort update
    try:
        conn.execute(
            update(api_keys)
            .where(api_keys.c.id == row["id"])
            .values(last_used_at=_now_utc())
        )
    except Exception:
        pass

    return {
        "api_key_id": row["id"],
        "name": row["name"],
        "scopes": row.get("scopes"),
    }
