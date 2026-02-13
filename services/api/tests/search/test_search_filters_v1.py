import pytest
from packages.domain.search.filters import SearchFiltersV1


def test_filters_empty_ok():
    f = SearchFiltersV1.model_validate({})
    assert f.language is None
    assert f.to_opensearch_filters() == []
    assert f.to_qdrant_filter() is None


def test_filters_language_source_compile():
    f = SearchFiltersV1.model_validate({"language": "en", "source": "whisper"})
    osf = f.to_opensearch_filters()
    assert {"term": {"language": "en"}} in osf
    assert {"term": {"source": "whisper"}} in osf

    qf = f.to_qdrant_filter()
    assert qf is not None
    must = qf["must"]
    assert {"key": "language", "match": {"value": "en"}} in must
    assert {"key": "source", "match": {"value": "whisper"}} in must


def test_date_range_validation():
    with pytest.raises(ValueError):
        SearchFiltersV1.model_validate(
            {"date_from": "2026-01-02T00:00:00Z", "date_to": "2026-01-01T00:00:00Z"}
        )


def test_date_range_compiles():
    f = SearchFiltersV1.model_validate(
        {"date_from": "2026-01-01T00:00:00Z", "date_to": "2026-01-02T00:00:00Z"}
    )
    osf = f.to_opensearch_filters()
    assert any("range" in x for x in osf)

    qf = f.to_qdrant_filter()
    assert qf is not None
    assert any(x.get("key") == "created_at_ms" for x in qf["must"])
