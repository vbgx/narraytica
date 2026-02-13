from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

MAX_LIMIT = 100


class SearchFiltersV1(BaseModel):
    language: str | None = None
    source: str | None = None
    video_id: str | None = None
    speaker_id: str | None = None
    date_from: str | None = None
    date_to: str | None = None


class SearchRequestV1(BaseModel):
    # Strict V1 (matches JSON schema)
    query: str | None = None
    filters: SearchFiltersV1 | None = None
    limit: int = Field(default=20, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)
    mode: Literal["lexical", "semantic", "hybrid"] | None = None


class SearchRequestCompat(SearchRequestV1):
    # Compat-only extras (NOT in schema)
    semantic: bool | None = None
    weights: dict[str, Any] | None = None
    filters: SearchFiltersV1 | dict[str, Any] | None = None
