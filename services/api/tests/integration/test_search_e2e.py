from __future__ import annotations

import importlib
import os
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.opensearch_integration

OS_URL = os.environ.get("OPENSEARCH_URL", "http://127.0.0.1:9200").rstrip("/")
INDEX = os.environ.get("OPENSEARCH_SEGMENTS_INDEX", "narralytica-segments-v1").strip()

VID = "video_01"
SID1 = "seg_01"
SID2 = "seg_02"


def seed_opensearch(
    *,
    created_at_1: str = "2026-01-01T00:00:00Z",
    created_at_2: str = "2026-01-02T00:00:00Z",
):
    """
    Seed OpenSearch with segments that are valid for the /search response contract.

    Required by API mapping:
    - video_id
    - start_ms
    - end_ms
    - text
    """
    c = httpx.Client(timeout=10)

    # (Re)create index with minimal mapping needed by the API.
    # Delete is best-effort: index may not exist.
    c.delete(f"{OS_URL}/{INDEX}")

    r = c.put(
        f"{OS_URL}/{INDEX}",
        json={
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": {
                "properties": {
                    "video_id": {"type": "keyword"},
                    "transcript_id": {"type": "keyword"},
                    "speaker_id": {"type": "keyword"},
                    "segment_index": {"type": "integer"},
                    "start_ms": {"type": "integer"},
                    "end_ms": {"type": "integer"},
                    "text": {"type": "text"},
                    "language": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                }
            },
        },
    )
    r.raise_for_status()

    # Index docs (IDs are segment IDs, as used by the API)
    c.post(
        f"{OS_URL}/{INDEX}/_doc/{SID1}",
        json={
            "video_id": VID,
            "start_ms": 0,
            "end_ms": 1000,
            "text": "hello world",
            "language": "en",
            "source": "whisper",
            "created_at": created_at_1,
            "updated_at": created_at_1,
        },
    ).raise_for_status()

    c.post(
        f"{OS_URL}/{INDEX}/_doc/{SID2}",
        json={
            "video_id": VID,
            "start_ms": 1000,
            "end_ms": 2000,
            "text": "bonjour le monde",
            "language": "fr",
            "source": "whisper",
            "created_at": created_at_2,
            "updated_at": created_at_2,
        },
    ).raise_for_status()

    c.post(f"{OS_URL}/{INDEX}/_refresh").raise_for_status()


def client():
    import services.api.src.config as cfg
    import services.api.src.main as main_mod
    import services.api.src.routes.search as search_mod

    importlib.reload(cfg)
    importlib.reload(search_mod)
    importlib.reload(main_mod)

    app = main_mod.create_app()

    # Override auth for integration tests: search is tested separately from auth.
    import services.api.src.auth.deps as auth_deps

    def _fake_require_api_key() -> dict[str, Any]:
        return {"api_key_id": "test_key", "name": "tests", "scopes": None}

    app.dependency_overrides[auth_deps.require_api_key] = _fake_require_api_key

    return TestClient(app, raise_server_exceptions=True)


def test_keyword_hit():
    seed_opensearch()

    c = client()
    r = c.post("/api/v1/search", json={"query": "hello", "mode": "lexical"})
    assert r.status_code == 200, r.text

    ids = [i["segment"]["id"] for i in r.json()["items"]]
    assert SID1 in ids


def test_filter_language():
    seed_opensearch()

    c = client()
    r = c.post(
        "/api/v1/search",
        json={"query": "", "filters": {"language": "fr"}, "mode": "lexical"},
    )
    assert r.status_code == 200, r.text

    ids = [i["segment"]["id"] for i in r.json()["items"]]
    assert SID2 in ids
    assert SID1 not in ids


def test_filter_date_narrows():
    seed_opensearch(
        created_at_1="2026-01-01T00:00:00Z",
        created_at_2="2026-01-10T00:00:00Z",
    )

    c = client()
    r = c.post(
        "/api/v1/search",
        json={
            "query": "",
            "filters": {"date_from": "2026-01-05T00:00:00Z"},
            "mode": "lexical",
        },
    )
    assert r.status_code == 200, r.text

    ids = [i["segment"]["id"] for i in r.json()["items"]]
    assert SID2 in ids
    assert SID1 not in ids


def test_merge_no_duplicates(monkeypatch):
    seed_opensearch()

    c = client()

    class _VHit:
        def __init__(self, segment_id: str, score: float):
            self.segment_id = segment_id
            self.score = score

    def fake_vector_search(*, query_text: str, filters: dict, top_k: int):
        return [_VHit(SID1, 0.99), _VHit(SID2, 0.98)]

    import services.api.src.routes.search as search_routes

    monkeypatch.setattr(search_routes, "vector_search", fake_vector_search)

    r = c.post("/api/v1/search", json={"query": "hello", "mode": "hybrid"})
    assert r.status_code == 200, r.text

    ids = [i["segment"]["id"] for i in r.json()["items"]]
    assert len(ids) == len(set(ids))


def test_vector_disabled_no_crash():
    seed_opensearch()

    c = client()
    r = c.post("/api/v1/search", json={"query": "hello", "mode": "lexical"})
    assert r.status_code == 200, r.text
