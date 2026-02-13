from __future__ import annotations

from packages.search.types import SearchFilters
from packages.search_infra.qdrant_filter import build_qdrant_filter


def test_build_qdrant_filter_none_when_empty():
    assert build_qdrant_filter(None) is None
    assert build_qdrant_filter(SearchFilters()) is None


def test_build_qdrant_filter_terms_present():
    f = SearchFilters(language="fr", source="yt", video_id="v1", speaker_id="s1")
    out = build_qdrant_filter(f)
    assert out and "must" in out
    must = out["must"]
    assert {"key": "language", "match": {"value": "fr"}} in must
    assert {"key": "source", "match": {"value": "yt"}} in must
    assert {"key": "video_id", "match": {"value": "v1"}} in must
    assert {"key": "speaker_id", "match": {"value": "s1"}} in must
