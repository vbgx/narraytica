from __future__ import annotations

from typing import Any

from packages.search.ports import SearchQueryNormalized


def build_lexical_query_body(q: SearchQueryNormalized, *, top_k: int) -> dict[str, Any]:
    must: list[dict[str, Any]] = []

    if q.query:
        must.append({"match": {"text": {"query": q.query}}})
    else:
        must.append({"match_all": {}})

    f = q.filters
    if f:
        if f.language:
            must.append({"term": {"language": f.language}})
        if f.source:
            must.append({"term": {"source": f.source}})
        if f.video_id:
            must.append({"term": {"video_id": f.video_id}})
        if f.speaker_id:
            must.append({"term": {"speaker_id": f.speaker_id}})
        if f.date_from or f.date_to:
            r: dict[str, Any] = {}
            if f.date_from:
                r["gte"] = f.date_from
            if f.date_to:
                r["lte"] = f.date_to
            must.append({"range": {"created_at": r}})

    return {
        "size": int(top_k),
        "query": {"bool": {"must": must}},
        "highlight": {"fields": {"text": {}}},
    }
