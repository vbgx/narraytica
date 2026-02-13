from __future__ import annotations

from .errors import BadQuery
from .types import SearchFilters, SearchMode, SearchQuery

MAX_LIMIT = 100


def normalize_query(q: SearchQuery) -> SearchQuery:
    """
    Single source of truth for SearchQueryV1 semantics.

    Contract constraints enforced:
    - limit must be 1..100
    - offset must be >= 0
    - query is stripped; empty -> null
    - filters fields are scalars in V1
    - date_from/date_to are strings|null
      (ordering validation is deferred)
    """
    limit = int(q.limit)
    offset = int(q.offset)

    if limit < 1 or limit > MAX_LIMIT:
        raise BadQuery("limit must be between 1 and 100")

    if offset < 0:
        raise BadQuery("offset must be >= 0")

    query = _normalize_query_text(q.query)
    mode = _normalize_mode(q.mode)
    filters = _normalize_filters(q.filters)

    return SearchQuery(
        query=query,
        limit=limit,
        offset=offset,
        mode=mode,
        filters=filters,
    )


def _normalize_query_text(s: str | None) -> str | None:
    if s is None:
        return None
    t = s.strip()
    return t or None


def _normalize_mode(m: SearchMode | None) -> SearchMode | None:
    if m is None:
        return None
    if m not in ("lexical", "semantic", "hybrid"):
        raise BadQuery("mode must be one of: lexical, semantic, hybrid, or null")
    return m


def _normalize_filters(f: SearchFilters | None) -> SearchFilters | None:
    if f is None:
        return None

    def _clean(x: str | None) -> str | None:
        if x is None:
            return None
        t = x.strip()
        return t or None

    return SearchFilters(
        language=_clean(f.language),
        source=_clean(f.source),
        video_id=_clean(f.video_id),
        speaker_id=_clean(f.speaker_id),
        date_from=_clean(f.date_from),
        date_to=_clean(f.date_to),
    )
