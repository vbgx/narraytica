from __future__ import annotations

import pytest
from packages.search.errors import BadQuery
from packages.search.filters import normalize_query
from packages.search.types import SearchFilters, SearchQuery


def test_normalize_query_clamps_limit_and_strips_query():
    q = SearchQuery(
        query="  hello  ",
        limit=100,
        offset=0,
        mode="hybrid",
        filters=None,
    )
    nq = normalize_query(q)
    assert nq.query == "hello"
    assert nq.limit == 100


def test_normalize_query_rejects_limit_out_of_range():
    with pytest.raises(BadQuery):
        normalize_query(
            SearchQuery(
                query="hello",
                limit=0,
                offset=0,
                mode="hybrid",
                filters=None,
            )
        )

    with pytest.raises(BadQuery):
        normalize_query(
            SearchQuery(
                query="hello",
                limit=101,
                offset=0,
                mode="hybrid",
                filters=None,
            )
        )


def test_normalize_query_rejects_negative_offset():
    with pytest.raises(BadQuery):
        normalize_query(
            SearchQuery(
                query="hello",
                limit=10,
                offset=-1,
                mode="hybrid",
                filters=None,
            )
        )


def test_normalize_filters_strips_and_nullifies_empties():
    q = SearchQuery(
        query="hello",
        limit=10,
        offset=0,
        mode="hybrid",
        filters=SearchFilters(
            language="  fr ",
            source="",
            video_id="  ",
            speaker_id=None,
            date_from=" 2020-01-01T00:00:00Z ",
            date_to="",
        ),
    )

    nq = normalize_query(q)
    assert nq.filters is not None
    assert nq.filters.language == "fr"
    assert nq.filters.source is None
    assert nq.filters.video_id is None
    assert nq.filters.date_from == "2020-01-01T00:00:00Z"
    assert nq.filters.date_to is None
