from __future__ import annotations

from services.api.src.domain.search_filters import SearchFiltersV1


def build_qdrant_filter(filters: dict | None) -> dict | None:
    f = SearchFiltersV1.model_validate(filters or {})
    return f.to_qdrant_filter()
