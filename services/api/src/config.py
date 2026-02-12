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
    # Existing settings (keep what you need)
    opensearch_url: str | None = os.environ.get("OPENSEARCH_URL")
    opensearch_segments_index: str | None = os.environ.get("OPENSEARCH_SEGMENTS_INDEX")

    # Redis (optional)
    redis_url: str | None = os.environ.get("REDIS_URL")

    # Rate limit
    rate_limit_enabled: bool = _env_bool("RATE_LIMIT_ENABLED", True)
    rate_limit_limit: int = _env_int("RATE_LIMIT_LIMIT", 60)
    rate_limit_window_seconds: int = _env_int("RATE_LIMIT_WINDOW_SECONDS", 60)
    rate_limit_path_prefix: str = os.environ.get("RATE_LIMIT_PATH_PREFIX", "/api/")


settings = Settings()
