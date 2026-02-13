from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from packages.application.errors import AppError
from packages.application.search.dtos import SearchQueryDTO
from packages.application.search.use_case import SearchDeps, execute
from pydantic import BaseModel, Field

from services.api.src.search.adapter import (
    opensearch_mget,
    opensearch_search,
    vector_search_safe,
)
from services.api.src.search.hybrid.merge import merge_results
from services.api.src.search.opensearch.lexical_query import build_lexical_query
from services.api.src.search.qdrant.vector_search import (
    vector_search as _vector_search_impl,
)

router = APIRouter(prefix="/search", tags=["search"])
MAX_LIMIT = 100


# ---------------------------------------------------------------------------
# Test patch points (compat surface)
# ---------------------------------------------------------------------------
def _opensearch_search(body):
    return opensearch_search(body)


def _opensearch_mget(ids):
    return opensearch_mget(ids)


def vector_search(*, query_text: str, filters: dict | None, top_k: int):
    """
    Patch point used by integration tests.
    Default implementation uses the real qdrant vector_search.
    """
    return _vector_search_impl(query_text=query_text, filters=filters, top_k=top_k)


# ---------------------------------------------------------------------------
# HTTP models (API layer only)
# ---------------------------------------------------------------------------
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


def _http_from_app_error(e: AppError) -> HTTPException:
    status = 500
    if e.code == "validation_error":
        status = 400
    elif e.code == "not_found":
        status = 404
    elif e.code == "conflict":
        status = 409
    elif e.code == "unauthorized":
        status = 401
    elif e.code == "forbidden":
        status = 403
    elif e.code == "unavailable":
        status = 503
    return HTTPException(
        status_code=status,
        detail={"code": e.code, "message": e.message, "details": e.details},
    )


# ---------------------------------------------------------------------------
# Ports wiring (API glue)
# ---------------------------------------------------------------------------
class _LexicalAdapter:
    def search(self, *, body):
        return _opensearch_search(body)


class _SegmentsAdapter:
    def mget(self, *, ids):
        return _opensearch_mget(ids)


class _VectorAdapter:
    def search(self, *, query_text: str, filters: dict | None, top_k: int):
        # Preserve existing prod behavior: swallow vector errors.
        # BUT use `vector_search` patch point for tests.
        try:
            v = vector_search(query_text=query_text, filters=filters, top_k=top_k)

            out = []
            for x in v:
                if isinstance(x, dict):
                    sid = x.get("segment_id") or x.get("id")
                    score = x.get("score")
                else:
                    sid = getattr(x, "segment_id", None)
                    score = getattr(x, "score", None)

                if sid is None or score is None:
                    continue
                out.append({"segment_id": str(sid), "score": float(score)})

            return out
        except Exception:
            # keep swallow semantics from prior behavior
            return vector_search_safe(
                query_text=query_text,
                filters=filters,
                top_k=top_k,
            )


class _MergeAdapter:
    def merge(self, *, lexical, vector):
        return merge_results(lexical=lexical, vector=vector)


def _to_dto(req: SearchRequestV1) -> SearchQueryDTO:
    return SearchQueryDTO(
        query=req.query,
        filters=(req.filters.model_dump(exclude_none=True) if req.filters else None),
        limit=int(req.limit),
        offset=int(req.offset),
        mode=req.mode,
        semantic=req.semantic,
    )


def _run(req: SearchRequestV1) -> dict:
    try:
        out = execute(
            req=_to_dto(req),
            deps=SearchDeps(
                lexical=_LexicalAdapter(),
                segments=_SegmentsAdapter(),
                vector=_VectorAdapter(),
                merger=_MergeAdapter(),
                build_lexical_query=build_lexical_query,
            ),
        )
        return out.data
    except AppError as e:
        raise _http_from_app_error(e) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.post("")
def search_post(req: SearchRequestV1) -> dict:
    return _run(req)


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
    return _run(req)
