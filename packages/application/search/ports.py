from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class VectorHit:
    segment_id: str
    score: float


class SearchInfraPort(Protocol):
    def opensearch_search(
        self, body: dict[str, Any]
    ) -> tuple[
        list[dict[str, Any]],
        dict[str, dict],
        dict[str, Any],
        dict[str, list[dict[str, Any]]],
    ]: ...

    def opensearch_mget(self, ids: list[str]) -> dict[str, dict]: ...

    def vector_search(
        self, *, query_text: str, filters: dict | None, top_k: int
    ) -> list[VectorHit]: ...
