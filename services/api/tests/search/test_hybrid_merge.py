from services.api.src.search.hybrid.merge import merge_results


def test_merge_empty():
    out = merge_results(lexical=[], vector=[])
    assert out == []


def test_merge_disjoint_no_duplicates():
    lexical = [{"segment_id": "a"}, {"segment_id": "b"}]
    vector = [{"segment_id": "c"}, {"segment_id": "d"}]
    out = merge_results(lexical=lexical, vector=vector)

    ids = [x.segment_id for x in out]
    assert len(ids) == len(set(ids))
    assert set(ids) == {"a", "b", "c", "d"}


def test_merge_overlap_prioritized():
    lexical = [{"segment_id": "a"}, {"segment_id": "b"}, {"segment_id": "c"}]
    vector = [{"segment_id": "c"}, {"segment_id": "b"}, {"segment_id": "x"}]
    out = merge_results(lexical=lexical, vector=vector)

    ids = [x.segment_id for x in out]
    assert ids[0] in {"b", "c"}
    assert "b" in ids and "c" in ids


def test_merge_is_deterministic():
    lexical = [{"segment_id": "b"}, {"segment_id": "a"}]
    vector = [{"segment_id": "a"}]
    out1 = merge_results(lexical=lexical, vector=vector)
    out2 = merge_results(lexical=lexical, vector=vector)

    assert [x.segment_id for x in out1] == [x.segment_id for x in out2]
    assert [x.score for x in out1] == [x.score for x in out2]
