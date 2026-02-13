from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from .types import SearchFilters, SearchItem, SearchQuery

# ============================================================================
# Normalized Query (engine-facing)
# ============================================================================


@dataclass(frozen=True)
class SearchQueryNormalized:
    """
    Engine-facing normalized query.

    Invariants:
    - limit: 1..100
    - offset: >=0
    - query stripped (None allowed)
    - filters normalized (trimmed, empty->None)
    """

    query: str | None
    limit: int
    offset: int
    mode: str  # "lexical" | "semantic" | "hybrid"
    filters: SearchFilters | None


# ============================================================================
# Intermediate Hits (backend-facing)
# ============================================================================


@dataclass(frozen=True)
class LexicalHit:
    """
    Minimal hit returned by lexical backend adapter.

    Invariants expected by merge:
    - segment.id is stable and unique
    - score_lexical is monotonic w.r.t lexical ranking (higher is better)
    - item is contract-shaped (segment required, score present)
    """

    item: SearchItem
    score_lexical: float
    lexical_rank: int | None = None


@dataclass(frozen=True)
class VectorHit:
    """
    Minimal hit returned by vector backend adapter.

    Invariants expected by merge:
    - segment.id is stable and unique
    - score_vector is monotonic w.r.t similarity (higher is better)
    """

    item: SearchItem
    score_vector: float
    vector_rank: int | None = None


@dataclass(frozen=True)
class LexicalResult:
    """
    Lexical search output.

    Note:
    - total is optional; in V1, SearchPage.total may be null.
    - items may be > limit; engine controls pagination after merge.
    """

    hits: Sequence[LexicalHit]
    total: int | None = None


@dataclass(frozen=True)
class VectorResult:
    hits: Sequence[VectorHit]
    total: int | None = None


# ============================================================================
# Ports
# ============================================================================


class LexicalSearchPort(Protocol):
    def search_lexical(self, q: SearchQueryNormalized) -> LexicalResult: ...


class VectorSearchPort(Protocol):
    def search_vector(self, q: SearchQueryNormalized) -> VectorResult: ...


class HybridMergePort(Protocol):
    """
    Merge contract.

    Must be deterministic:
    - dedup by segment.id
    - stable tie-break
    - produces contract-compliant SearchResult (types)
    """

    def merge(
        self,
        *,
        q: SearchQueryNormalized,
        lexical: LexicalResult,
        vector: VectorResult,
    ) -> list[SearchItem]: ...


# Backward-compat: keep SearchEngine entrypoint signature stable
SearchEngineQuery = SearchQuery
