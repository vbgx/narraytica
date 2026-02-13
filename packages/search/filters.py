from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

from .errors import BadQuery
from .types import SearchFilters, SearchMode, SearchQuery

MAX_LIMIT = 100

_ALLOWED_FILTER_KEYS = {
    "language",
    "source",
    "video_id",
    "speaker_id",
    "date_from",
    "date_to",
}


def normalize_query(q: SearchQuery) -> SearchQuery:
    """
    Single source of truth for SearchQueryV1 semantics.

    Contract constraints enforced:
    - limit must be 1..100
    - offset must be >= 0
    - query is stripped; empty -> null
    - filters fields are scalars in V1 (no lists)
    - date_from/date_to are ISO strings|null (validated + ordered)
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


def normalize_filters_dict(raw: dict[str, Any] | None) -> SearchFilters | None:
    """
    Strict normalization from a legacy flexible dict (HTTP/app layer).

    Rules:
    - unknown keys => BadQuery (prevents invisible drift)
    - values must be scalars (string or null) for V1
    - applies the same normalization/validation as normalize_query()
    """
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise BadQuery("filters must be an object or null")

    unknown = set(raw.keys()) - _ALLOWED_FILTER_KEYS
    if unknown:
        raise BadQuery("unknown filter key(s)", details={"unknown": sorted(unknown)})

    f = SearchFilters(
        language=raw.get("language"),
        source=raw.get("source"),
        video_id=raw.get("video_id"),
        speaker_id=raw.get("speaker_id"),
        date_from=raw.get("date_from"),
        date_to=raw.get("date_to"),
    )
    return _normalize_filters(f)


def normalized_query_to_dict(q: SearchQuery) -> dict[str, Any]:
    """
    Helper for golden tests: normalized query -> stable JSONable dict.
    """
    out = {
        "query": q.query,
        "limit": q.limit,
        "offset": q.offset,
        "mode": q.mode,
        "filters": None if q.filters is None else asdict(q.filters),
    }
    # Drop null filter fields for stable snapshots (optional).
    if out["filters"] is not None:
        out["filters"] = {k: v for k, v in out["filters"].items() if v is not None}
    return out


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
        if not isinstance(x, str):
            raise BadQuery("filter values must be strings or null")
        t = x.strip()
        return t or None

    language = _clean(f.language)
    if language is not None and len(language) < 2:
        raise BadQuery("filters.language must be at least 2 characters")

    date_from = _clean(f.date_from)
    date_to = _clean(f.date_to)

    # Validate ISO format (best effort, strict enough to catch garbage).
    df = _parse_iso(date_from) if date_from is not None else None
    dt = _parse_iso(date_to) if date_to is not None else None
    if df is not None and dt is not None and df > dt:
        raise BadQuery("filters.date_from must be <= filters.date_to")

    return SearchFilters(
        language=language.lower() if language is not None else None,
        source=_clean(f.source),
        video_id=_clean(f.video_id),
        speaker_id=_clean(f.speaker_id),
        date_from=date_from,
        date_to=date_to,
    )


def _parse_iso(s: str) -> datetime:
    # Accept trailing "Z" as UTC.
    try:
        if s.endswith("Z"):
            s2 = s[:-1] + "+00:00"
        else:
            s2 = s
        dt = datetime.fromisoformat(s2)
        if dt.tzinfo is None:
            # Assume UTC if tz missing (contract says ISO string; UTC recommended).
            dt = dt.replace(tzinfo=UTC)
        return dt
    except Exception as e:
        raise BadQuery("invalid ISO datetime", details={"value": s}) from e
