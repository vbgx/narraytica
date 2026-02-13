from __future__ import annotations

from typing import Any, Literal, TypedDict

# =============================================================================
# Shared
# =============================================================================


class PageDTO(TypedDict):
    limit: int
    offset: int


class AppErrorDTO(TypedDict, total=False):
    """
    Boundary-friendly error payload (NOT an HTTP error).
    Routes decide how to map these to HTTP status codes.
    """

    code: str
    message: str
    details: Any


# =============================================================================
# SEARCH DTOs
# =============================================================================


class SearchQueryDTO(TypedDict, total=False):
    """
    Contract-first shape.

    Expected (aligned with your contract tests drift you saw):
    - q: str
    - page: {limit, offset} (required)
    - filters: free-form object (optional)
    """

    q: str
    page: PageDTO
    filters: dict[str, Any]
    options: dict[str, Any]


class SearchItemScoreDTO(TypedDict, total=False):
    """
    Contract-first: score is an object, not a float.
    Required field in your recent contract failures: combined.
    """

    combined: float
    lexical: float
    semantic: float


class SearchItemDTO(TypedDict):
    id: str
    type: str
    score: SearchItemScoreDTO
    payload: dict[str, Any]


class SearchResultDTO(TypedDict, total=False):
    page: PageDTO
    total: int
    items: list[SearchItemDTO]


# =============================================================================
# JOBS DTOs
# =============================================================================

JobStatus = Literal["queued", "running", "succeeded", "failed", "canceled"]


class CreateJobDTO(TypedDict, total=False):
    """
    Minimal job creation request shape.
    Keep it thin; actual canonical fields must come from contracts.
    """

    kind: str
    input: dict[str, Any]
    options: dict[str, Any]
    idempotency_key: str


class JobStatusDTO(TypedDict, total=False):
    job_id: str
    status: JobStatus
    created_at: str
    updated_at: str
    result: dict[str, Any]
    error: AppErrorDTO


class JobEventDTO(TypedDict, total=False):
    job_id: str
    seq: int
    ts: str
    type: str
    payload: dict[str, Any]


# =============================================================================
# INGEST DTOs
# =============================================================================


class IngestRequestDTO(TypedDict, total=False):
    """
    Request shape for ingest entrypoint.
    """

    source: str
    media: dict[str, Any]
    metadata: dict[str, Any]
    options: dict[str, Any]
    idempotency_key: str


class IngestResultDTO(TypedDict, total=False):
    """
    Response shape for ingest.
    Usually returns a job handle or direct artifact refs.
    """

    job: JobStatusDTO
    artifacts: list[dict[str, Any]]
    warnings: list[AppErrorDTO]
