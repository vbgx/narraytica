from __future__ import annotations

import os
from hashlib import sha256
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError

from ..domain.search_filters import SearchFiltersV1
from ..search.hybrid.merge import merge_results
from ..search.opensearch.lexical_query import build_lexical_query
from ..search.qdrant.vector_search import (
    VectorSearchError,
    vector_search,
)

router = APIRouter(prefix="/search", tags=["search"])

MAX_LIMIT = 100


class SearchRequest(BaseModel):
    query: str | None = Field(default=None)
    filters: dict | None = Field(default=None)
    limit: int = Field(default=20, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)
    semantic: bool | None = Field(default=None)


class SearchHit(BaseModel):
    segment_id: str
    score: float
    lexical_rank: int | None = None
    vector_rank: int | None = None
    source: dict[str, Any] | None = None


class SearchResponse(BaseModel):
    items: list[SearchHit]
    limit: int
    offset: int
    total: int


def _opensearch_url() -> str:
    url = os.environ.get("OPENSEARCH_URL")
    if not url:
        raise HTTPException(
            status_code=503,
            detail="OpenSearch not configured",
        )
    return url.rstrip("/")


def _segments_index() -> str:
    return os.environ.get(
        "OPENSEARCH_SEGMENTS_INDEX",
        "narralytica-it-segments",
    )


def parse_search_filters(
    filters: dict | None,
) -> SearchFiltersV1:
    try:
        return SearchFiltersV1.model_validate(filters or {})
    except (ValidationError, ValueError) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e


def _query_fingerprint(q: str) -> str:
    return sha256(q.encode()).hexdigest()[:12]


def _opensearch_search(
    body: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict]]:
    url = f"{_opensearch_url()}/{_segments_index()}/_search"

    auth = None
    user = os.environ.get("OPENSEARCH_USERNAME")
    pwd = os.environ.get("OPENSEARCH_PASSWORD")
    if user and pwd:
        auth = (user, pwd)

    try:
        r = requests.post(
            url,
            json=body,
            timeout=10,
            auth=auth,
        )
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"OpenSearch unavailable: {e}",
        ) from e

    hits = (((data or {}).get("hits") or {}).get("hits")) or []

    lexical: list[dict[str, Any]] = []
    sources: dict[str, dict] = {}

    for h in hits:
        sid = h.get("_id")
        if not sid:
            continue
        sid = str(sid)
        lexical.append({"segment_id": sid})
        src = h.get("_source")
        if isinstance(src, dict):
            sources[sid] = src

    return lexical, sources


def _run_search(req: SearchRequest) -> SearchResponse:

    query_text = (req.query or "").strip()
    semantic = req.semantic if req.semantic is not None else bool(query_text)

    f = parse_search_filters(req.filters)

    if semantic and not query_text:
        raise HTTPException(
            status_code=400,
            detail="semantic search requires a query",
        )

    fetch_n = min(MAX_LIMIT, req.limit + req.offset)

    lexical_body = build_lexical_query(
        query=query_text or None,
        filters={"__compiled__": f.to_opensearch_filters()},
        limit=fetch_n,
        offset=0,
    )

    lexical_hits, sources = _opensearch_search(lexical_body)

    vector_hits: list[dict[str, Any]] = []

    if semantic:
        try:
            v = vector_search(
                query_text=query_text,
                filters=f.model_dump(exclude_none=True),
                top_k=fetch_n,
            )
            vector_hits = [{"segment_id": x.segment_id, "score": x.score} for x in v]
        except VectorSearchError:
            # degrade gracefully
            vector_hits = []

    merged = merge_results(
        lexical=lexical_hits,
        vector=vector_hits,
    )

    page = merged[req.offset : req.offset + req.limit]

    items = [
        SearchHit(
            segment_id=x.segment_id,
            score=x.score,
            lexical_rank=x.lexical_rank,
            vector_rank=x.vector_rank,
            source=sources.get(x.segment_id),
        )
        for x in page
    ]

    return SearchResponse(
        items=items,
        limit=req.limit,
        offset=req.offset,
        total=len(merged),
    )


@router.post("", response_model=SearchResponse)
def search_post(req: SearchRequest) -> SearchResponse:
    return _run_search(req)


@router.get("", response_model=SearchResponse)
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
) -> SearchResponse:
    req = SearchRequest(
        query=q,
        filters={
            "language": language,
            "source": source,
            "video_id": video_id,
            "speaker_id": speaker_id,
            "date_from": date_from,
            "date_to": date_to,
        },
        limit=limit,
        offset=offset,
        semantic=semantic,
    )
    return _run_search(req)
