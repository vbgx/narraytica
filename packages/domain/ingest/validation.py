from __future__ import annotations

from typing import Any


class IngestValidationError(ValueError):
    """
    Domain-level validation error.

    Must NOT depend on FastAPI or any HTTP framework.
    API layer is responsible for mapping this to HTTPException.
    """

    pass


def validate_ingest_payload(payload: dict[str, Any]) -> None:
    """
    Pure domain validation for ingest request.

    Raises:
        IngestValidationError if payload is invalid.
    """

    if not isinstance(payload, dict):
        raise IngestValidationError("payload must be an object")

    source = payload.get("source")
    if not isinstance(source, dict):
        raise IngestValidationError("source must be an object")

    kind = source.get("kind")
    if not kind:
        raise IngestValidationError("source.kind is required")

    if kind == "external_url":
        url = source.get("url")
        if not isinstance(url, str) or not url.strip():
            raise IngestValidationError("source.url is required for external_url")

    # Add future invariant rules here (pure domain only)
