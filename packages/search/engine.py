from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from .errors import BackendUnavailable
from .filters import normalize_query
from .ranking import MergeWeights, merge_hybrid_items
from .types import SearchItem, SearchPage, SearchQuery, SearchResult


class LexicalPort(Protocol):
    def search_lexical(self, query: SearchQuery) -> Sequence[SearchItem]: ...


class SemanticPort(Protocol):
    def search_semantic(self, query: SearchQuery) -> Sequence[SearchItem]: ...


@dataclass
class SearchEngine:
    """
    Canonical SearchEngine API (contracts-first).

    Invariants:
    - No HTTP exceptions
    - No backend clients imported
    - Uses ports only
    """

    lexical: LexicalPort | None = None
    semantic: SemanticPort | None = None
    weights: MergeWeights = MergeWeights()

    def search(self, query: SearchQuery) -> SearchResult:
        q = normalize_query(query)

        mode = q.mode or "hybrid"

        if mode == "lexical":
            if self.lexical is None:
                raise BackendUnavailable("lexical backend not configured")
            items = list(self.lexical.search_lexical(q))
            total = len(items)
            sliced = items[q.offset : q.offset + q.limit]
            return SearchResult(
                items=list(sliced),
                page=SearchPage(limit=q.limit, offset=q.offset, total=total),
            )

        if mode == "semantic":
            if self.semantic is None:
                raise BackendUnavailable("semantic backend not configured")
            items = list(self.semantic.search_semantic(q))
            total = len(items)
            sliced = items[q.offset : q.offset + q.limit]
            return SearchResult(
                items=list(sliced),
                page=SearchPage(limit=q.limit, offset=q.offset, total=total),
            )

        # hybrid
        if self.lexical is None or self.semantic is None:
            raise BackendUnavailable(
                "hybrid mode requires both lexical and semantic backends"
            )

        lex = list(self.lexical.search_lexical(q))
        sem = list(self.semantic.search_semantic(q))

        merged_all = merge_hybrid_items(lex, sem, weights=self.weights)

        total = len(
            merged_all
        )  # V1 allows total null; we provide deterministic union count
        sliced = merged_all[q.offset : q.offset + q.limit]
        return SearchResult(
            items=list(sliced),
            page=SearchPage(limit=q.limit, offset=q.offset, total=total),
        )
