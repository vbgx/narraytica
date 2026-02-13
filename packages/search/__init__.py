"""
packages.search — canonical search behavior (contracts-first).

Single source of truth for:
- SearchQuery/SearchResult core types (aligned with JSON Schemas)
- filter semantics + normalization
- hybrid merge / ranking

No HTTP. No backend clients. Ports only.
"""

from .engine import SearchEngine
from .errors import (
    BackendUnavailable,
    BadQuery,
    ContractsMismatch,
    SearchError,
    UnsupportedFilter,
)
from .types import (
    SearchFilters,
    SearchHighlight,
    SearchItem,
    SearchPage,
    SearchQuery,
    SearchResult,
    SearchScore,
    SearchSegment,
    SearchSpeaker,
    SearchVideo,
)

__all__ = [
    "SearchEngine",
    "SearchQuery",
    "SearchFilters",
    "SearchResult",
    "SearchItem",
    "SearchPage",
    "SearchScore",
    "SearchSegment",
    "SearchVideo",
    "SearchSpeaker",
    "SearchHighlight",
    "SearchError",
    "BadQuery",
    "UnsupportedFilter",
    "BackendUnavailable",
    "ContractsMismatch",
]
