from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

SearchMode = Literal["lexical", "semantic", "hybrid"]


@dataclass(frozen=True)
class SearchQueryDTO:
    query: str | None
    filters: dict[str, Any] | None
    limit: int
    offset: int
    mode: SearchMode | None
    semantic: bool | None  # legacy compatibility


@dataclass(frozen=True)
class SearchResultDTO:
    data: dict[str, Any]
