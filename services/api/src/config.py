from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        return default


@dataclass(frozen=True)
class Settings:
    """
    Settings contract (anti-drift):

    Canonical DB env var:
      - DATABASE_URL

    Backward compatible alias:
      - API_DATABASE_URL

    We expose both:
      - settings.database_url (canonical)
      - settings.api_database_url (compat alias)
    """

    # ----------------------------
    # Database (canonical + compat)
    # ----------------------------
    database_url: str | None = os.environ.get("DATABASE_URL") or None
    api_database_url: str | None = os.environ.get("API_DATABASE_URL") or None

    # ----------------------------
    # OpenSearch
    # ----------------------------
    opensearch_url: str | None = os.environ.get("OPENSEARCH_URL") or None
    opensearch_segments_index: str | None = (
        os.environ.get("OPENSEARCH_SEGMENTS_INDEX") or None
    )

    # ----------------------------
    # Redis (optional)
    # ----------------------------
    redis_url: str | None = os.environ.get("REDIS_URL") or None

    # ----------------------------
    # Rate limit
    # ----------------------------
    rate_limit_enabled: bool = _env_bool("RATE_LIMIT_ENABLED", True)
    rate_limit_limit: int = _env_int("RATE_LIMIT_LIMIT", 60)
    rate_limit_window_seconds: int = _env_int("RATE_LIMIT_WINDOW_SECONDS", 60)
    rate_limit_path_prefix: str = os.environ.get("RATE_LIMIT_PATH_PREFIX", "/api/")

    @property
    def db_url(self) -> str | None:
        """
        Single source of truth for DB URL at runtime.
        Prefer DATABASE_URL, fallback to API_DATABASE_URL.
        """
        return self.database_url or self.api_database_url


settings = Settings()
