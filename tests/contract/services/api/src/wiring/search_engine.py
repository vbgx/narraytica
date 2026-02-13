from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import services.api.src.routes.search as search_routes
from packages.application.search.dtos import SearchQueryDTO
from packages.application.search.use_case import execute
from packages.search.mapping import result_from_dict
from packages.search.types import SearchQuery
from services.api.src.wiring.search_deps import build_search_deps


def _canonical_to_dto(q: SearchQuery) -> SearchQueryDTO:
    filters = None
    if q.filters is not None:
        filters = {
            "language": q.filters.language,
            "source": q.filters.source,
            "video_id": q.filters.video_id,
            "speaker_id": q.filters.speaker_id,
            "date_from": q.filters.date_from,
            "date_to": q.filters.date_to,
        }
        filters = {k: v for k, v in filters.items() if v is not None}

    return SearchQueryDTO(
        query=q.query,
        filters=filters,
        limit=int(q.limit),
        offset=int(q.offset),
        mode=q.mode,
        semantic=None,
    )


@dataclass
class ContractEngine:
    def search(self, q: SearchQuery) -> Any:
        deps = build_search_deps(
            opensearch_search_fn=search_routes._opensearch_search,
            opensearch_mget_fn=search_routes._opensearch_mget,
            vector_impl=search_routes.vector_search,
        )
        out = execute(req=_canonical_to_dto(q), deps=deps)
        return result_from_dict(out.data)


def build_engine() -> Any:
    return ContractEngine()
