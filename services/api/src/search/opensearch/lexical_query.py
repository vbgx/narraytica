from __future__ import annotations

from typing import Any

MAX_LIMIT = 100
DEFAULT_LIMIT = 20


def clamp_limit(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_LIMIT
    return max(1, min(int(limit), MAX_LIMIT))


def build_lexical_query(
    *,
    query: str | None,
    filters: dict | None,
    limit: int | None,
    offset: int | None,
) -> dict[str, Any]:
    size = clamp_limit(limit)
    from_ = max(0, int(offset or 0))

    must: list[dict] = []
    filter_clauses: list[dict] = []

    if query and query.strip():
        must.append(
            {
                "multi_match": {
                    "query": query,
                    "fields": ["text^3", "text.prefix"],
                    "type": "best_fields",
                    "operator": "and",
                }
            }
        )

    if filters:
        compiled = filters.get("__compiled__")
        if isinstance(compiled, list):
            filter_clauses.extend(compiled)
        else:
            if filters.get("language"):
                filter_clauses.append({"term": {"language": filters["language"]}})
            if filters.get("source"):
                filter_clauses.append({"term": {"source": filters["source"]}})
            if filters.get("video_id"):
                filter_clauses.append({"term": {"video_id": filters["video_id"]}})
            if filters.get("speaker_id"):
                filter_clauses.append({"term": {"speaker_id": filters["speaker_id"]}})

            date_range: dict[str, Any] = {}
            if filters.get("date_from"):
                date_range["gte"] = filters["date_from"]
            if filters.get("date_to"):
                date_range["lt"] = filters["date_to"]
            if date_range:
                filter_clauses.append({"range": {"created_at": date_range}})

    if must or filter_clauses:
        query_block = {
            "bool": {
                "must": must if must else [{"match_all": {}}],
                "filter": filter_clauses,
            }
        }
    else:
        query_block = {"match_all": {}}

    return {
        "from": from_,
        "size": size,
        "query": query_block,
        "sort": [
            {"_score": {"order": "desc"}},
            {"created_at": {"order": "desc"}},
            {"id": {"order": "asc"}},
        ],
    }
