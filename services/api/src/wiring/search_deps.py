from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from packages.application.search.use_case import SearchDeps
from packages.search.ranking import MergeWeights, merge_ranked_ids
from services.api.src.search.adapter import vector_search_safe
from services.api.src.search.opensearch.lexical_query import build_lexical_query

VectorSearchFn = Callable[..., Any]
OpenSearchSearchFn = Callable[..., Any]
OpenSearchMgetFn = Callable[..., Any]


class _LexicalAdapter:
    def __init__(self, *, search_fn: OpenSearchSearchFn):
        self._search_fn = search_fn

    def search(self, *, body):
        return self._search_fn(body)


class _SegmentsAdapter:
    def __init__(self, *, mget_fn: OpenSearchMgetFn):
        self._mget_fn = mget_fn

    def mget(self, *, ids):
        return self._mget_fn(ids)


class _VectorAdapter:
    def __init__(self, *, impl: VectorSearchFn):
        self._impl = impl

    def search(self, *, query_text: str, filters: dict | None, top_k: int):
        try:
            v = self._impl(query_text=query_text, filters=filters, top_k=top_k)

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
                query_text=query_text,
                filters=filters,
                top_k=top_k,
            )


@dataclass(frozen=True)
class HybridItem:
    segment_id: str
    score: float
    lexical_rank: int | None
    vector_rank: int | None


class _MergeAdapter:
    def __init__(self, *, weights: MergeWeights | None = None):
        self._weights = weights or MergeWeights()

    def merge(self, *, lexical, vector):
        lexical = lexical or []
        vector = vector or []

        lex_ids: list[str] = []
        vec_ids: list[str] = []

        for it in lexical:
            if not isinstance(it, dict):
                continue
            sid = it.get("segment_id") or it.get("id")
            if sid is None:
                continue
            lex_ids.append(str(sid))

        for it in vector:
            if not isinstance(it, dict):
                continue
            sid = it.get("segment_id") or it.get("id")
            if sid is None:
                continue
            vec_ids.append(str(sid))

        merged = merge_ranked_ids(
            lexical_ids=lex_ids,
            vector_ids=vec_ids,
            weights=self._weights,
        )

        out: list[HybridItem] = []
        for x in merged:
            out.append(
                HybridItem(
                    segment_id=x.segment_id,
                    score=float(x.score),
                    lexical_rank=x.lexical_rank,
                    vector_rank=x.vector_rank,
                )
            )
        return out


def build_search_deps(
    *,
    opensearch_search_fn: OpenSearchSearchFn,
    opensearch_mget_fn: OpenSearchMgetFn,
    vector_impl: VectorSearchFn,
    weights: MergeWeights | None = None,
) -> SearchDeps:
    return SearchDeps(
        lexical=_LexicalAdapter(search_fn=opensearch_search_fn),
        segments=_SegmentsAdapter(mget_fn=opensearch_mget_fn),
        vector=_VectorAdapter(impl=vector_impl),
        merger=_MergeAdapter(weights=weights),
        build_lexical_query=build_lexical_query,
    )
