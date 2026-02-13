from __future__ import annotations

from pathlib import Path

from ._helpers import load_json, load_schema, validate_payload


def test_search_query_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/search_query.sample.json"))
    schema = load_schema("search_query.schema.json")
    validate_payload(schema=schema, payload=payload)


def test_search_response_fixture_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/search_result.sample.json"))
    schema = load_schema("search.schema.json")
    validate_payload(schema=schema, payload=payload)


def test_runtime_search_result_mapping_matches_contract():
    from packages.search.response import to_dict
    from packages.search.types import (
        SearchItem,
        SearchPage,
        SearchResult,
        SearchScore,
        SearchSegment,
    )

    result = SearchResult(
        items=[
            SearchItem(
                segment=SearchSegment(
                    id="seg_1",
                    video_id="vid_1",
                    start_ms=0,
                    end_ms=1000,
                    text="hello",
                ),
                score=SearchScore(combined=1.0),
                video=None,
                speaker=None,
                highlights=[],
            )
        ],
        page=SearchPage(limit=20, offset=0, total=1),
    )

    payload = to_dict(result)
    schema = load_schema("search.schema.json")
    validate_payload(schema=schema, payload=payload)
