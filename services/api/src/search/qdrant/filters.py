from __future__ import annotations

from typing import Any


def build_qdrant_filter(filters: dict | None) -> dict[str, Any] | None:
    if not filters:
        return None

    must: list[dict[str, Any]] = []

    def term(key: str, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str) and not value.strip():
            return
        must.append({"key": key, "match": {"value": value}})

    term("language", filters.get("language"))
    term("source", filters.get("source"))
    term("video_id", filters.get("video_id"))
    term("speaker_id", filters.get("speaker_id"))

    if filters.get("date_from") or filters.get("date_to"):
        raise ValueError(
            "date_from/date_to are not supported for vector search in v1 "
            "(created_at is stored as keyword in Qdrant payload)"
        )

    if not must:
        return None

    return {"must": must}
