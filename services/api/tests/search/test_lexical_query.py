from services.api.src.search.opensearch.lexical_query import (
    build_lexical_query,
)


def test_basic_query():
    q = build_lexical_query(
        query="hello world",
        filters=None,
        limit=10,
        offset=0,
    )

    assert q["size"] == 10
    assert q["from"] == 0
    assert q["query"]["bool"]["must"][0]["multi_match"]["query"] == "hello world"


def test_filter_only_query():
    q = build_lexical_query(
        query=None,
        filters={"language": "en"},
        limit=20,
        offset=0,
    )

    must = q["query"]["bool"]["must"]
    filters = q["query"]["bool"]["filter"]

    assert must == [{"match_all": {}}]
    assert {"term": {"language": "en"}} in filters


def test_query_and_filters():
    q = build_lexical_query(
        query="search text",
        filters={"video_id": "vid_123"},
        limit=5,
        offset=10,
    )

    assert q["from"] == 10
    assert q["size"] == 5
    assert {"term": {"video_id": "vid_123"}} in q["query"]["bool"]["filter"]


def test_limit_clamped():
    q = build_lexical_query(
        query="x",
        filters=None,
        limit=1000,
        offset=0,
    )

    assert q["size"] <= 100
