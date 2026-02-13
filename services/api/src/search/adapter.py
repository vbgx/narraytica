from __future__ import annotations

from typing import Any

from services.infra.search_backends.qdrant.vector_search import (
    VectorSearchError,
    vector_search,
)


def vector_search_safe(
    *,
    query_text: str,
    filters: dict | None,
    top_k: int,
) -> list[dict[str, Any]]:
    try:
        v = vector_search(query_text=query_text, filters=filters, top_k=top_k)
        return [{"segment_id": x.segment_id, "score": x.score} for x in v]
    except VectorSearchError:
        return []
