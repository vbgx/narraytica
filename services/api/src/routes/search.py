from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from ..domain.search_filters import SearchFiltersV1
from ..search.opensearch.lexical_query import build_lexical_query

router = APIRouter(prefix="/search", tags=["search"])


def parse_search_filters(filters: dict | None) -> SearchFiltersV1:
    try:
        return SearchFiltersV1.model_validate(filters or {})
    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("")
def search(
    q: str | None = Query(default=None),
    language: str | None = Query(default=None),
    source: str | None = Query(default=None),
    video_id: str | None = Query(default=None),
    speaker_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    limit: int | None = Query(default=20, ge=1, le=100),
    offset: int | None = Query(default=0, ge=0),
) -> dict[str, Any]:
    f = parse_search_filters(
        {
            "language": language,
            "source": source,
            "video_id": video_id,
            "speaker_id": speaker_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )

    body = build_lexical_query(
        query=q,
        filters={"__compiled__": f.to_opensearch_filters()},
        limit=limit,
        offset=offset,
    )

    return {
        "lexical_query": body,
        "filters": f.model_dump(exclude_none=True),
    }
