from __future__ import annotations

from packages.search.ports import LexicalHit, LexicalResult, VectorHit, VectorResult
from packages.search.ranking import MergeWeights, merge_hybrid
from packages.search.types import SearchItem, SearchScore, SearchSegment


def _item(seg_id: str) -> SearchItem:
    return SearchItem(
        segment=SearchSegment(
            id=seg_id,
            video_id="vid",
            start_ms=0,
            end_ms=1000,
            text="x",
        ),
        score=SearchScore(combined=0.0),
        video=None,
        speaker=None,
        highlights=[],
    )


def test_merge_dedups_by_segment_id_and_is_deterministic():
    lex = LexicalResult(
        hits=[
            LexicalHit(item=_item("s1"), score_lexical=10.0, lexical_rank=1),
            LexicalHit(item=_item("s2"), score_lexical=9.0, lexical_rank=2),
        ]
    )
    vec = VectorResult(
        hits=[
            VectorHit(item=_item("s1"), score_vector=0.2, vector_rank=5),
            VectorHit(item=_item("s3"), score_vector=0.9, vector_rank=1),
        ]
    )

    out = merge_hybrid(
        lexical=lex,
        vector=vec,
        weights=MergeWeights(lexical=1.0, vector=1.0),
    )

    assert [it.segment.id for it in out] == ["s1", "s2", "s3"]

    s1 = out[0]
    assert s1.segment.id == "s1"
    assert s1.score.combined == 10.2
    assert s1.score.lexical == 10.0
    assert s1.score.vector == 0.2
    assert s1.score.lexical_rank == 1
    assert s1.score.vector_rank == 5


def test_merge_tiebreak_is_id_asc_when_equal_combined():
    lex = LexicalResult(
        hits=[
            LexicalHit(item=_item("b"), score_lexical=1.0),
            LexicalHit(item=_item("a"), score_lexical=1.0),
        ]
    )
    vec = VectorResult(hits=[])

    out = merge_hybrid(
        lexical=lex,
        vector=vec,
        weights=MergeWeights(lexical=1.0, vector=0.0),
    )
    assert [it.segment.id for it in out] == ["a", "b"]
