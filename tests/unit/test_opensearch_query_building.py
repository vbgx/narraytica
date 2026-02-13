from __future__ import annotations

from packages.search.ports import SearchQueryNormalized
from packages.search.types import SearchFilters
from packages.search_infra.opensearch_query import build_lexical_query_body


def test_build_lexical_query_body_contains_filters():
    q = SearchQueryNormalized(
        query="hello",
        limit=10,
        offset=5,
        mode="hybrid",
        filters=SearchFilters(
            language="fr",
            source="yt",
            video_id="vid1",
            speaker_id="spk1",
            date_from="2024-01-01T00:00:00Z",
            date_to="2024-01-31T00:00:00Z",
        ),
    )

    body = build_lexical_query_body(q, top_k=15)
    assert body["size"] == 15

    must = body["query"]["bool"]["must"]
    assert {"term": {"language": "fr"}} in must
    assert {"term": {"source": "yt"}} in must
    assert {"term": {"video_id": "vid1"}} in must
    assert {"term": {"speaker_id": "spk1"}} in must
    assert any("range" in x for x in must)
