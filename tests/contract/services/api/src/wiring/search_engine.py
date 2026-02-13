from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from packages.application.search.dtos import SearchQueryDTO
from packages.application.search.use_case import SearchDeps, execute
from packages.search.mapping import result_from_dict
from packages.search.types import SearchQuery
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


# Patch points (kept for integration tests)
def _opensearch_search(body):
    return opensearch_search(body)


def _opensearch_mget(ids):
    return opensearch_mget(ids)


def vector_search(*, query_text: str, filters: dict | None, top_k: int):
    return _vector_search_impl(query_text=query_text, filters=filters, top_k=top_k)


class _LexicalAdapter:
    def search(self, *, body):
        return _opensearch_search(body)


class _SegmentsAdapter:
    def mget(self, *, ids):
        return _opensearch_mget(ids)


class _VectorAdapter:
    def search(self, *, query_text: str, filters: dict | None, top_k: int):
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
            return vector_search_safe(
                query_text=query_text, filters=filters, top_k=top_k
            )


class _MergeAdapter:
    def merge(self, *, lexical, vector):
        return merge_results(lexical=lexical, vector=vector)


def _canonical_to_legacy_dto(q: SearchQuery) -> SearchQueryDTO:
    """
    Temporary delegation mapper (Phase 3.2).
    Canonical contracts -> legacy application DTO.
    """
    filters = None
    if q.filters is not None:
        filters = {
            "language": q.filters.language,
            "source": q.filters.source,
            "video_id": q.filters.video_id,
            "speaker_id": q.filters.speaker_id,
            "date_from": q.filters.date_from,
            "date_to": q.filters.date_to,
        }
        filters = {k: v for k, v in filters.items() if v is not None}

    # semantic legacy: express ONLY via mode (avoid dual truth)
    semantic = None

    return SearchQueryDTO(
        query=q.query,
        filters=filters,
        limit=int(q.limit),
        offset=int(q.offset),
        mode=q.mode,
        semantic=semantic,
    )


@dataclass
class LegacyDelegatingEngine:
    """
    Implements canonical SearchEngine API by delegating to legacy application execute().

    Goal: keep production working while moving semantics into packages/search.
    """

    def search(self, q: SearchQuery):
        out = execute(
            req=_canonical_to_legacy_dto(q),
            deps=SearchDeps(
                lexical=_LexicalAdapter(),
                segments=_SegmentsAdapter(),
                vector=_VectorAdapter(),
                merger=_MergeAdapter(),
                build_lexical_query=build_lexical_query,
            ),
        )
        # Drift firewall: map dict -> canonical types or explode (CI catches)
        return result_from_dict(out.data)


def build_engine() -> Any:
    # Return object with .search(SearchQuery)->SearchResult
    return LegacyDelegatingEngine()
