from __future__ import annotations

from typing import Any, Protocol


class LexicalSearchPort(Protocol):
    def search(
        self, *, body: dict[str, Any]
    ) -> tuple[
        list[dict[str, Any]],  # lexical hits
        dict[str, dict],  # sources by id
        dict[str, Any],  # lexical_scores by id
        dict[str, list[dict[str, Any]]],  # highlights already contract-shaped
    ]: ...


class SegmentsPort(Protocol):
    def mget(self, *, ids: list[str]) -> dict[str, dict]: ...


class VectorSearchPort(Protocol):
    def search(
        self, *, query_text: str, filters: dict | None, top_k: int
    ) -> list[dict[str, Any]]: ...


class MergePort(Protocol):
    def merge(
        self,
        *,
        lexical: list[dict[str, Any]] | None,
        vector: list[dict[str, Any]] | None,
    ): ...
