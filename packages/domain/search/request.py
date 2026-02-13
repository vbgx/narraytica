from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SearchWeightsIn(BaseModel):
    lexical: float | None = None
    semantic: float | None = None


class SearchRequestIn(BaseModel):
    query: str | None = None
    limit: int = 20
    offset: int = 0
    mode: str | None = None
    semantic: bool | None = None

    weights: SearchWeightsIn | None = None

    # Filters intentionally flexible.
    # A stricter contract may live in domain/search_filters.py.
    filters: dict[str, Any] | None = None
