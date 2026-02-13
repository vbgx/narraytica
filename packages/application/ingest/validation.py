from __future__ import annotations

from urllib.parse import urlparse

from ..errors import AppError


def normalize_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise AppError(code="validation_error", message="url is required")
    u = url.strip()
    p = urlparse(u)
    if p.scheme not in ("http", "https"):
        raise AppError(code="validation_error", message="url must be http(s)")
    if not p.netloc:
        raise AppError(code="validation_error", message="url is missing host")
    return u


def validate_source_fields(source: str, payload: dict) -> None:
    if not source or not isinstance(source, str):
        raise AppError(code="validation_error", message="source is required")
    if not isinstance(payload, dict):
        raise AppError(code="validation_error", message="payload must be an object")
    # Keep thin. Add strict per-source rules here (migrated from API domain).
