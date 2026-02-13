from services.api.src.search.opensearch.lexical_query import build_lexical_query


def test_build_lexical_query_match_all_when_empty():
    q = build_lexical_query(query=None, filters=None, limit=20, offset=0)
    assert q["query"] == {"match_all": {}}
    assert q["size"] == 20
    assert q["from"] == 0
    assert q["sort"][-1] == {"_id": {"order": "asc"}}


def test_build_lexical_query_compiles_filters():
    q = build_lexical_query(
        query="hello",
        filters={"language": "fr", "video_id": "v1"},
        limit=10,
        offset=5,
    )
    boolq = q["query"]["bool"]
    assert boolq["must"][0]["multi_match"]["query"] == "hello"
    filters = boolq["filter"]
    assert {"term": {"language": "fr"}} in filters
    assert {"term": {"video_id": "v1"}} in filters
