from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

from ..config import settings

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is not None:
        return _engine

    database_url = settings.api_database_url
    if not database_url:
        raise RuntimeError("API_DATABASE_URL is required (settings.api_database_url)")

    _engine = create_engine(
        database_url,
        pool_pre_ping=True,
        future=True,
    )
    return _engine


def get_conn() -> Iterator[Connection]:
    engine = get_engine()
    with engine.begin() as conn:
        yield conn
