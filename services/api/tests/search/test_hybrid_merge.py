from packages.search.ranking import merge_ranked_ids


def test_hybrid_merge_deterministic_ordering():
    lexical = [{"segment_id": "a"}, {"segment_id": "b"}, {"segment_id": "c"}]
    vector = [{"segment_id": "b"}, {"segment_id": "c"}, {"segment_id": "d"}]

    lex_ids = [x["segment_id"] for x in lexical]
    vec_ids = [x["segment_id"] for x in vector]

    merged = merge_ranked_ids(lexical_ids=lex_ids, vector_ids=vec_ids)

    assert [x.segment_id for x in merged] == sorted(
        [x.segment_id for x in merged],
        key=lambda sid: (-next(it.score for it in merged if it.segment_id == sid), sid),
    )
