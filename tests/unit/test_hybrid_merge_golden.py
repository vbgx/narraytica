from __future__ import annotations

import json
from pathlib import Path

from services.api.src.search.hybrid.merge import merge_results

FIX_QUERIES = Path("tests/fixtures/search/queries")
GOLDEN = Path("tests/fixtures/search/golden")


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)


def _to_dicts(items):
    return [
        {
            "segment_id": x.segment_id,
            "score": float(x.score),
            "lexical_rank": x.lexical_rank,
            "vector_rank": x.vector_rank,
        }
        for x in items
    ]


def test_hybrid_merge_basic_golden():
    inp = _load(FIX_QUERIES / "03_hybrid_merge_basic.json")
    got = merge_results(
        lexical=inp["lexical"],
        vector=inp["vector"],
        weight_lexical=inp["weight_lexical"],
        weight_vector=inp["weight_vector"],
    )
    exp = _load(GOLDEN / "03_hybrid_merge_basic.merged.json")
    assert _dump(_to_dicts(got)) == _dump(exp)


def test_hybrid_merge_tie_break_is_segment_id_golden():
    inp = _load(FIX_QUERIES / "04_hybrid_merge_tie.json")
    got = merge_results(
        lexical=inp["lexical"],
        vector=inp["vector"],
        weight_lexical=inp["weight_lexical"],
        weight_vector=inp["weight_vector"],
    )
    exp = _load(GOLDEN / "04_hybrid_merge_tie.merged.json")
    assert _dump(_to_dicts(got)) == _dump(exp)
