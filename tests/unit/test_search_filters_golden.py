from __future__ import annotations

import json
from pathlib import Path

import pytest
from services.api.src.search.opensearch.lexical_query import build_lexical_query
from services.api.src.search.qdrant.filters import build_qdrant_filter

FIX_QUERIES = Path("tests/fixtures/search/queries")
GOLDEN = Path("tests/fixtures/search/golden")


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)


def test_lexical_query_multilingual_golden():
    inp = _load(FIX_QUERIES / "01_multilingual.json")
    got = build_lexical_query(
        query=inp.get("query"),
        filters=inp.get("filters"),
        limit=inp.get("limit"),
        offset=inp.get("offset"),
    )
    exp = _load(GOLDEN / "01_multilingual.lexical_query.json")
    assert _dump(got) == _dump(exp)


def test_lexical_query_speaker_timewindow_golden():
    inp = _load(FIX_QUERIES / "02_speaker_timewindow.json")
    got = build_lexical_query(
        query=inp.get("query"),
        filters=inp.get("filters"),
        limit=inp.get("limit"),
        offset=inp.get("offset"),
    )
    exp = _load(GOLDEN / "02_speaker_timewindow.lexical_query.json")
    assert _dump(got) == _dump(exp)


def test_qdrant_filter_rejects_date_range_semantics():
    inp = _load(FIX_QUERIES / "02_speaker_timewindow.json")
    with pytest.raises(ValueError):
        build_qdrant_filter(inp["filters"])
