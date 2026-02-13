from __future__ import annotations

from typing import Any

from packages.search.types import SearchFilters


def build_qdrant_filter(filters: SearchFilters | None) -> dict[str, Any] | None:
    if filters is None:
        return None

    must: list[dict[str, Any]] = []

    def term(key: str, value: str) -> None:
        must.append({"key": key, "match": {"value": value}})

    if filters.language:
        term("language", filters.language)
    if filters.source:
        term("source", filters.source)
    if filters.video_id:
        term("video_id", filters.video_id)
    if filters.speaker_id:
        term("speaker_id", filters.speaker_id)

    if filters.date_from or filters.date_to:
        r: dict[str, Any] = {}
        if filters.date_from:
            r["gte"] = filters.date_from
        if filters.date_to:
            r["lte"] = filters.date_to
        must.append({"key": "created_at", "range": r})

    if not must:
        return None

    return {"must": must}
