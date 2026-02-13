from __future__ import annotations

from typing import Any


def build_qdrant_filter(filters: dict | None) -> dict[str, Any] | None:
    """
    Infra function.
    Accepts raw dict filters (already parsed upstream).

    Contract (tests):
    - Reject date ranges (date_from/date_to) because Qdrant payload filtering
      isn't supported/defined yet.
    - No import from services/api/src/domain/*
    """
    if not filters or not isinstance(filters, dict):
        return None

    # Explicitly reject date ranges (stable behavior, no silent ignoring)
    if filters.get("date_from") or filters.get("date_to"):
        raise ValueError("date range filtering is not supported for vector search")

    must: list[dict[str, Any]] = []

    if filters.get("language"):
        must.append({"key": "language", "match": {"value": filters["language"]}})

    if filters.get("source"):
        must.append({"key": "source", "match": {"value": filters["source"]}})

    if filters.get("video_id"):
        must.append({"key": "video_id", "match": {"value": filters["video_id"]}})

    if filters.get("speaker_id"):
        must.append({"key": "speaker_id", "match": {"value": filters["speaker_id"]}})

    if not must:
        return None

    return {"must": must}
