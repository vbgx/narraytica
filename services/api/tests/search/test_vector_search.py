import pytest
from services.api.src.search.qdrant.filters import build_qdrant_filter
from services.api.src.search.qdrant.vector_search import (
    VectorSearchError,
    clamp_top_k,
    vector_search,
)


def test_clamp_top_k():
    assert clamp_top_k(None) == 10
    assert clamp_top_k(0) == 1
    assert clamp_top_k(1) == 1
    assert clamp_top_k(999) == 50


def test_build_qdrant_filter_terms():
    f = build_qdrant_filter(
        {"language": "en", "source": "whisper", "video_id": "v1", "speaker_id": "s1"}
    )
    assert f is not None
    must = f["must"]
    assert {"key": "language", "match": {"value": "en"}} in must
    assert {"key": "source", "match": {"value": "whisper"}} in must
    assert {"key": "video_id", "match": {"value": "v1"}} in must
    assert {"key": "speaker_id", "match": {"value": "s1"}} in must


def test_build_qdrant_filter_rejects_date_range():
    with pytest.raises(ValueError):
        build_qdrant_filter({"date_from": "2026-01-01T00:00:00Z"})


def test_vector_search_errors_clean_when_embeddings_missing(monkeypatch):
    monkeypatch.delenv("EMBEDDINGS_URL", raising=False)

    with pytest.raises(VectorSearchError) as e:
        vector_search(query_text="hello", filters=None, top_k=5)

    assert "Embeddings provider not configured" in str(e.value)
