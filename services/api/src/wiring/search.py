from __future__ import annotations

from collections.abc import Callable
from typing import Any

from packages.application.search.dtos import SearchQueryDTO
from packages.application.search.use_case import execute
from services.api.src.wiring.search_deps import build_search_deps

OpenSearchSearchFn = Callable[[dict[str, Any]], Any]
OpenSearchMgetFn = Callable[[list[str]], Any]
VectorSearchFn = Callable[..., Any]


def run_search(
    req: SearchQueryDTO,
    *,
    opensearch_search_fn: OpenSearchSearchFn | None = None,
    opensearch_mget_fn: OpenSearchMgetFn | None = None,
    vector_impl: VectorSearchFn | None = None,
) -> dict:
    """
    API wiring: builds concrete deps (OpenSearch/Qdrant) and runs application use-case.

    Tests may pass overrides (monkeypatched functions from routes) to keep stability.
    """
    if opensearch_search_fn is None or opensearch_mget_fn is None:
        from services.api.src.search.adapter import opensearch_mget as _os_mget_impl
        from services.api.src.search.adapter import opensearch_search as _os_search_impl

        opensearch_search_fn = opensearch_search_fn or _os_search_impl
        opensearch_mget_fn = opensearch_mget_fn or _os_mget_impl

    if vector_impl is None:
        from services.api.src.search.qdrant.vector_search import (
            vector_search as _vector_search_impl,
        )

        vector_impl = _vector_search_impl

    out = execute(
        req=req,
        deps=build_search_deps(
            opensearch_search_fn=opensearch_search_fn,
            opensearch_mget_fn=opensearch_mget_fn,
            vector_impl=vector_impl,
        ),
    )
    return out.data
