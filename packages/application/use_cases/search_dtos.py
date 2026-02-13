from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class SearchPageDTO(TypedDict):
    limit: int
    offset: int
    total: NotRequired[int | None]


class SearchHighlightDTO(TypedDict):
    field: Literal["text", "title", "speaker", "metadata"]
    text: str


class SearchSegmentDTO(TypedDict, total=False):
    id: str
    video_id: str
    transcript_id: str | None
    speaker_id: str | None
    segment_index: int | None
    start_ms: int
    end_ms: int
    text: str
    language: str | None
    source: str | None
    created_at: str | None
    updated_at: str | None


class SearchVideoDTO(TypedDict, total=False):
    id: str
    title: str | None
    source: str | None
    published_at: str | None


class SearchSpeakerDTO(TypedDict, total=False):
    id: str
    name: str | None


class SearchScoreDTO(TypedDict, total=False):
    combined: float
    lexical: float | None
    vector: float | None
    lexical_rank: int | None
    vector_rank: int | None


class SearchItemDTO(TypedDict, total=False):
    segment: SearchSegmentDTO
    video: SearchVideoDTO | None
    speaker: SearchSpeakerDTO | None
    highlights: list[SearchHighlightDTO] | None
    score: SearchScoreDTO


class SearchResponseDTO(TypedDict):
    items: list[SearchItemDTO]
    page: SearchPageDTO


# Request (contract-first minimal; we will add a JSON schema for it)
SearchMode = Literal["lexical", "semantic", "hybrid"]


class SearchFiltersDTO(TypedDict, total=False):
    language: str | None
    source: str | None
    video_id: str | None
    speaker_id: str | None
    date_from: str | None
    date_to: str | None


class SearchQueryDTO(TypedDict, total=False):
    query: str | None
    filters: SearchFiltersDTO | None
    limit: int
    offset: int
    mode: SearchMode | None
