from __future__ import annotations

from typing import Any

from ...domain.search_filters import SearchFiltersV1


def build_qdrant_filter(
    filters: dict[str, Any] | SearchFiltersV1,
) -> dict[str, Any] | None:
    """
    Build a Qdrant filter for vector search.

    Contract (as enforced by tests):
    - accepts raw dict or SearchFiltersV1
    - term filters only (language/source/video_id/speaker_id)
    - rejects date range filters (date_from/date_to)
    """
    if isinstance(filters, SearchFiltersV1):
        f = filters
    else:
        f = SearchFiltersV1.model_validate(filters or {})

    if f.date_from or f.date_to:
        raise ValueError("date range filters are not supported for vector search")

    must: list[dict[str, Any]] = []

    def term(key: str, value: str | None) -> None:
        if value is None:
            return
        must.append({"key": key, "match": {"value": value}})

    term("language", f.language)
    term("source", f.source)
    term("video_id", f.video_id)
    term("speaker_id", f.speaker_id)

    if not must:
        return None

    return {"must": must}
