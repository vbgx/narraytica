from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from packages.application.search.ports import SearchInfraPort, VectorHit
from packages.application.search.use_case import search_use_case
from pydantic import BaseModel, Field

from services.api.src.search.adapter import (
    opensearch_mget,
    opensearch_search,
    vector_search_safe,
)
from services.api.src.search.opensearch.lexical_query import build_lexical_query

router = APIRouter(prefix="/search", tags=["search"])
MAX_LIMIT = 100


class SearchFiltersModel(BaseModel):
    language: str | None = None
    source: str | None = None
    video_id: str | None = None
    speaker_id: str | None = None
    date_from: str | None = None
    date_to: str | None = None


class SearchRequestV1(BaseModel):
    query: str | None = Field(default=None)
    filters: SearchFiltersModel | None = Field(default=None)
    limit: int = Field(default=20, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)
    mode: Literal["lexical", "semantic", "hybrid"] | None = Field(default=None)
    semantic: bool | None = Field(default=None)


class Infra(SearchInfraPort):
    def opensearch_search(self, body):
        return opensearch_search(body)

    def opensearch_mget(self, ids):
        return opensearch_mget(ids)

    def vector_search(self, *, query_text, filters, top_k):
        hits = vector_search_safe(query_text=query_text, filters=filters, top_k=top_k)
        return [VectorHit(segment_id=x["segment_id"], score=x["score"]) for x in hits]


def _to_query_dict(req: SearchRequestV1) -> dict:
    return {
        "query": req.query,
        "filters": (req.filters.model_dump(exclude_none=True) if req.filters else None),
        "limit": int(req.limit),
        "offset": int(req.offset),
        "mode": req.mode,
        "semantic": req.semantic,
    }


@router.post("")
def search_post(req: SearchRequestV1) -> dict:
    try:
        return search_use_case(
            infra=Infra(),
            build_lexical_query=build_lexical_query,
            query=_to_query_dict(req),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.get("")
def search_get(
    q: str | None = Query(default=None),
    language: str | None = Query(default=None),
    source: str | None = Query(default=None),
    video_id: str | None = Query(default=None),
    speaker_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    semantic: bool | None = Query(default=None),
    mode: Literal["lexical", "semantic", "hybrid"] | None = Query(default=None),
) -> dict:
    req = SearchRequestV1(
        query=q,
        filters=SearchFiltersModel(
            language=language,
            source=source,
            video_id=video_id,
            speaker_id=speaker_id,
            date_from=date_from,
            date_to=date_to,
        ),
        limit=limit,
        offset=offset,
        semantic=semantic,
        mode=mode,
    )
    return search_post(req)
