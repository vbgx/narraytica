import json
from pathlib import Path

import pytest
from packages.search.filters import normalize_filters_dict, normalized_query_to_dict
from packages.search.types import SearchQuery

FIXTURES = Path("tests/fixtures/search/normalized")


def _load(name: str):
    return json.loads((FIXTURES / name).read_text())


def _dump(p):
    return json.dumps(p, indent=2, sort_keys=True) + "\n"


@pytest.mark.parametrize(
    "fixture_name",
    [
        "filters_golden_cases.json",
    ],
)
def test_filters_normalization_golden(fixture_name: str):
    payload = _load(fixture_name)

    out_cases = []
    for case in payload["cases"]:
        q = SearchQuery(
            query=case.get("query"),
            limit=int(case.get("limit", 20)),
            offset=int(case.get("offset", 0)),
            mode=case.get("mode"),
            filters=normalize_filters_dict(case.get("filters")),
        )
        out_cases.append(
            {
                "name": case["name"],
                "normalized": normalized_query_to_dict(q),
            }
        )

    golden_path = FIXTURES / "filters_golden.json"
    if not golden_path.exists():
        golden_path.write_text(_dump({"cases": out_cases}))
        raise AssertionError("Golden file created. Re-run tests.")

    assert json.loads(golden_path.read_text()) == {"cases": out_cases}
