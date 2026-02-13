from __future__ import annotations

from typing import Any


class SearchError(Exception):
    """
    Base error for search package.

    Invariants:
    - NEVER HTTPException
    - NEVER framework-specific
    - Messages must be safe to log.
    """

    code: str = "search_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class BadQuery(SearchError):
    code = "bad_query"


class UnsupportedFilter(SearchError):
    code = "unsupported_filter"


class BackendUnavailable(SearchError):
    code = "backend_unavailable"


class ContractsMismatch(SearchError):
    """
    Raised when Python types <-> JSON Schemas diverge (drift).
    This is a CI failure signal, not a runtime "user" error.
    """

    code = "contracts_mismatch"
