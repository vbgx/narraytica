from __future__ import annotations

from hashlib import sha256
from time import monotonic
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError

from ..config import settings
from ..domain.search_filters import SearchFiltersV1
from ..search.hybrid.merge import merge_results
from ..search.opensearch.lexical_query import build_lexical_query
from ..search.qdrant.vector_search import VectorSearchError, vector_search
from ..telemetry.logging import get_logger
from ..telemetry.request_context import get_request_id

router = APIRouter(prefix="/search", tags=["search"])
log = get_logger(__name__)

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


def parse_search_filters(filters: dict | None) -> SearchFiltersV1:
    try:
        return SearchFiltersV1.model_validate(filters or {})
    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def _query_fingerprint(q: str) -> str:
    h = sha256(q.encode("utf-8")).hexdigest()
    return h[:12]


def _opensearch_auth() -> tuple[str, str] | None:
    user = getattr(settings, "OPENSEARCH_USERNAME", None) or getattr(
        settings, "opensearch_username", None
    )
    pwd = getattr(settings, "OPENSEARCH_PASSWORD", None) or getattr(
        settings, "opensearch_password", None
    )
    if user and pwd:
        return (str(user), str(pwd))
    return None


def _opensearch_url() -> str:
    url = getattr(settings, "OPENSEARCH_URL", None) or getattr(
        settings, "opensearch_url", None
    )
    if not url:
        raise HTTPException(status_code=503, detail="OpenSearch not configured")
    return str(url).rstrip("/")


def _segments_index() -> str:
    return (
        getattr(settings, "OPENSEARCH_SEGMENTS_INDEX", None)
        or getattr(settings, "opensearch_segments_index", None)
        or "narralytica-segments-v1"
    )


def _request_timeout() -> float:
    t = getattr(settings, "OPENSEARCH_TIMEOUT_SECONDS", None) or getattr(
        settings, "opensearch_timeout_seconds", None
    )
    try:
        return float(t) if t is not None else 10.0
    except Exception:
        return 10.0


def _opensearch_search(
    body: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict], int]:
    url = f"{_opensearch_url()}/{_segments_index()}/_search"
    auth = _opensearch_auth()

    started = monotonic()
    try:
        r = requests.post(
            url,
            json=body,
            timeout=_request_timeout(),
            auth=auth,
        )
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"OpenSearch unavailable: {e}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"OpenSearch error: {e}",
        ) from e

    took_ms = int((monotonic() - started) * 1000.0)

    hits = (((data or {}).get("hits") or {}).get("hits")) or []
    lexical: list[dict[str, Any]] = []
    sources_by_id: dict[str, dict] = {}

    for h in hits:
        if not isinstance(h, dict):
            continue
        sid = h.get("_id") or (h.get("_source") or {}).get("id")
        if sid is None:
            continue
        sid_s = str(sid)
        lexical.append({"segment_id": sid_s})
        src = h.get("_source")
        if isinstance(src, dict):
            sources_by_id[sid_s] = src

    return lexical, sources_by_id, took_ms


def _run_search(req: SearchRequest) -> SearchResponse:
    rid = get_request_id()

    query_text = (req.query or "").strip()
    q_len = len(query_text)
    q_hash = _query_fingerprint(query_text) if query_text else None

    semantic = req.semantic
    if semantic is None:
        semantic = bool(query_text)

    filter_keys = sorted((req.filters or {}).keys())

    log.info(
        "search_request",
        extra={
            "request_id": rid,
            "query_len": q_len,
            "query_hash": q_hash,
            "semantic": semantic,
            "limit": req.limit,
            "offset": req.offset,
            "filter_keys": filter_keys,
        },
    )

    started_total = monotonic()
    f = parse_search_filters(req.filters)

    if semantic and not query_text:
        raise HTTPException(
            status_code=400,
            detail="semantic search requires a non-empty query",
        )

    fetch_n = min(MAX_LIMIT, req.limit + req.offset)

    lexical_body = build_lexical_query(
        query=query_text if query_text else None,
        filters={"__compiled__": f.to_opensearch_filters()},
        limit=fetch_n,
        offset=0,
    )

    lexical_hits, sources_by_id, took_os_ms = _opensearch_search(lexical_body)

    took_qdrant_ms = None
    vector_hits: list[dict[str, Any]] = []
    if semantic:
        v_started = monotonic()
        try:
            v = vector_search(
                query_text=query_text,
                filters=f.model_dump(exclude_none=True),
                top_k=fetch_n,
            )
            vector_hits = [{"segment_id": x.segment_id, "score": x.score} for x in v]
        except VectorSearchError as e:
            log.warning(
                "search_vector_unavailable",
                extra={
                    "request_id": rid,
                    "query_len": q_len,
                    "query_hash": q_hash,
                    "error": str(e),
                },
            )
            raise HTTPException(status_code=503, detail=str(e)) from e
        finally:
            took_qdrant_ms = int((monotonic() - v_started) * 1000.0)

    m_started = monotonic()
    merged = merge_results(lexical=lexical_hits, vector=vector_hits)
    took_merge_ms = int((monotonic() - m_started) * 1000.0)

    page = merged[req.offset : req.offset + req.limit]
    out_items: list[SearchHit] = []
    for it in page:
        out_items.append(
            SearchHit(
                segment_id=it.segment_id,
                score=it.score,
                lexical_rank=it.lexical_rank,
                vector_rank=it.vector_rank,
                source=sources_by_id.get(it.segment_id),
            )
        )

    took_total_ms = int((monotonic() - started_total) * 1000.0)

    log.info(
        "search_result",
        extra={
            "request_id": rid,
            "query_len": q_len,
            "query_hash": q_hash,
            "semantic": semantic,
            "filter_keys": filter_keys,
            "took_ms_total": took_total_ms,
            "took_ms_opensearch": took_os_ms,
            "took_ms_qdrant": took_qdrant_ms,
            "took_ms_merge": took_merge_ms,
            "lexical_count": len(lexical_hits),
            "vector_count": len(vector_hits),
            "merged_count": len(merged),
            "returned_count": len(out_items),
        },
    )

    return SearchResponse(
        items=out_items,
        limit=req.limit,
        offset=req.offset,
        total=len(merged),
    )


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


@router.post("", response_model=SearchResponse)
def search_post(req: SearchRequest) -> SearchResponse:
    return _run_search(req)
