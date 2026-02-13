from __future__ import annotations

import json
from pathlib import Path

from packages.search.filters import normalize_query, normalized_query_to_dict
from packages.search.types import SearchFilters, SearchQuery

FIX_QUERIES = Path("tests/fixtures/search/queries")
FIX_EXPECTED = Path("tests/fixtures/search/normalized")


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _to_query(payload: dict) -> SearchQuery:
    f = payload.get("filters")
    filters = None
    if isinstance(f, dict):
        filters = SearchFilters(
            language=f.get("language"),
            source=f.get("source"),
            video_id=f.get("video_id"),
            speaker_id=f.get("speaker_id"),
            date_from=f.get("date_from"),
            date_to=f.get("date_to"),
        )
    return SearchQuery(
        query=payload.get("query"),
        filters=filters,
        limit=int(payload["limit"]),
        offset=int(payload["offset"]),
        mode=payload.get("mode"),
    )


def test_filters_golden_multilang():
    inp = _load(FIX_QUERIES / "multilang.json")
    exp = _load(FIX_EXPECTED / "multilang.json")

    nq = normalize_query(_to_query(inp))
    got = normalized_query_to_dict(nq)
    assert got == exp


def test_filters_golden_speaker_time_window():
    inp = _load(FIX_QUERIES / "speaker_time_window.json")
    exp = _load(FIX_EXPECTED / "speaker_time_window.json")

    nq = normalize_query(_to_query(inp))
    got = normalized_query_to_dict(nq)
    assert got == exp
