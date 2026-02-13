from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SearchMode = Literal["lexical", "semantic", "hybrid"]


# =========================
# Query (SearchQueryV1)
# =========================


@dataclass(frozen=True)
class SearchFilters:
    """
    Contract: SearchQueryV1.filters

    additionalProperties: false
    All fields are nullable scalars in V1 (no arrays).
    """

    language: str | None = None
    source: str | None = None
    video_id: str | None = None
    speaker_id: str | None = None
    date_from: str | None = None  # ISO8601/RFC3339 string (schema: string|null)
    date_to: str | None = None  # ISO8601/RFC3339 string (schema: string|null)


@dataclass(frozen=True)
class SearchQuery:
    """
    Contract: SearchQueryV1

    IMPORTANT:
    - limit/offset are REQUIRED at root (not nested in `page`)
    - query can be null
    - mode can be null or enum
    """

    query: str | None
    limit: int
    offset: int
    mode: SearchMode | None = "hybrid"
    filters: SearchFilters | None = None


# =========================
# Response (SearchResponseV1)
# =========================


@dataclass(frozen=True)
class SearchScore:
    """
    Contract: SearchScore

    IMPORTANT:
    - combined is REQUIRED
    - lexical/vector scores are optional + nullable
    - ranks are optional + nullable (>=1)
    """

    combined: float
    lexical: float | None = None
    vector: float | None = None
    lexical_rank: int | None = None
    vector_rank: int | None = None


@dataclass(frozen=True)
class SearchSegment:
    """
    Contract: SearchSegment
    """

    id: str
    video_id: str
    start_ms: int
    end_ms: int
    text: str

    transcript_id: str | None = None
    speaker_id: str | None = None
    segment_index: int | None = None

    language: str | None = None
    source: str | None = None

    created_at: str | None = None
    updated_at: str | None = None


@dataclass(frozen=True)
class SearchVideo:
    """
    Contract: SearchVideo
    """

    id: str
    title: str | None = None
    source: str | None = None
    published_at: str | None = None


@dataclass(frozen=True)
class SearchSpeaker:
    """
    Contract: SearchSpeaker
    """

    id: str
    name: str | None = None


@dataclass(frozen=True)
class SearchHighlight:
    """
    Contract: SearchHighlight
    """

    field: Literal["text", "title", "speaker", "metadata"]
    text: str


@dataclass(frozen=True)
class SearchItem:
    """
    Contract: SearchResponseV1.$defs.item

    additionalProperties: false
    required: segment, score
    """

    segment: SearchSegment
    score: SearchScore
    video: SearchVideo | None = None
    speaker: SearchSpeaker | None = None
    highlights: list[SearchHighlight] | None = None


@dataclass(frozen=True)
class SearchPage:
    """
    Contract: SearchPage

    required: limit, offset
    total is optional + nullable in V1
    """

    limit: int
    offset: int
    total: int | None = None


@dataclass(frozen=True)
class SearchResult:
    """
    Contract: SearchResponseV1
    """

    items: list[SearchItem]
    page: SearchPage
