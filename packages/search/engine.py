from __future__ import annotations

from dataclasses import dataclass

from .errors import BackendUnavailable
from .filters import normalize_query
from .ports import (
    HybridMergePort,
    LexicalSearchPort,
    SearchQueryNormalized,
    VectorSearchPort,
)
from .ranking import MergeWeights, merge_hybrid
from .types import SearchItem, SearchPage, SearchQuery, SearchResult


@dataclass
class DefaultHybridMerger(HybridMergePort):
    weights: MergeWeights = MergeWeights()

    def merge(self, *, q: SearchQueryNormalized, lexical, vector) -> list[SearchItem]:
        # Pure merge; pagination handled by engine.
        return merge_hybrid(lexical=lexical, vector=vector, weights=self.weights)


@dataclass
class SearchEngine:
    """
    Canonical SearchEngine (contracts-first).

    Invariants:
    - No HTTP
    - No backend clients
    - Uses ports only
    """

    lexical: LexicalSearchPort | None = None
    vector: VectorSearchPort | None = None
    merger: HybridMergePort | None = None

    def search(self, query: SearchQuery) -> SearchResult:
        q0 = normalize_query(query)
        mode = q0.mode or "hybrid"

        q = SearchQueryNormalized(
            query=q0.query,
            limit=q0.limit,
            offset=q0.offset,
            mode=mode,
            filters=q0.filters,
        )

        if mode == "lexical":
            if self.lexical is None:
                raise BackendUnavailable("lexical backend not configured")
            lex = self.lexical.search_lexical(q)
            items = [h.item for h in lex.hits]
            total = lex.total if lex.total is not None else len(items)
            sliced = items[q.offset : q.offset + q.limit]
            return SearchResult(
                items=list(sliced),
                page=SearchPage(limit=q.limit, offset=q.offset, total=total),
            )

        if mode == "semantic":
            # Contract naming: schema uses "semantic" as mode; port is "vector".
            if self.vector is None:
                raise BackendUnavailable("vector backend not configured")
            vec = self.vector.search_vector(q)
            items = [h.item for h in vec.hits]
            total = vec.total if vec.total is not None else len(items)
            sliced = items[q.offset : q.offset + q.limit]
            return SearchResult(
                items=list(sliced),
                page=SearchPage(limit=q.limit, offset=q.offset, total=total),
            )

        # hybrid
        if self.lexical is None or self.vector is None:
            raise BackendUnavailable(
                "hybrid mode requires both lexical and vector backends"
            )

        lex = self.lexical.search_lexical(q)
        vec = self.vector.search_vector(q)

        merger = self.merger or DefaultHybridMerger()
        merged_all = merger.merge(q=q, lexical=lex, vector=vec)

        total = len(merged_all)
        sliced = merged_all[q.offset : q.offset + q.limit]
        return SearchResult(
            items=list(sliced),
            page=SearchPage(limit=q.limit, offset=q.offset, total=total),
        )
