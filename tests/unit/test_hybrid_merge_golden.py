import json
from pathlib import Path

from packages.search.ranking import merge_ranked_ids

FIXTURES = Path("tests/fixtures/search")


def _load(name: str):
    return json.loads((FIXTURES / name).read_text())


def test_hybrid_merge_golden_snapshot():
    payload = _load("hybrid_merge_cases.json")

    out = []
    for case in payload["cases"]:
        merged = merge_ranked_ids(
            lexical_ids=case.get("lexical_ids") or [],
            vector_ids=case.get("vector_ids") or [],
        )
        out.append(
            {
                "name": case["name"],
                "items": [
                    {
                        "segment_id": x.segment_id,
                        "score": x.score,
                        "lexical_rank": x.lexical_rank,
                        "vector_rank": x.vector_rank,
                    }
                    for x in merged
                ],
            }
        )

    golden_path = FIXTURES / "hybrid_merge_golden.json"
    if not golden_path.exists():
        golden_path.write_text(
            json.dumps({"cases": out}, indent=2, sort_keys=True) + "\n"
        )
        raise AssertionError("Golden file created. Re-run tests.")

    golden = json.loads(golden_path.read_text())
    assert golden == {"cases": out}
