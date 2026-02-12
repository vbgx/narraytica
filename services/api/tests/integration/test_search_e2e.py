from __future__ import annotations

import importlib
import os
import uuid
from typing import Any

import httpx
from fastapi.testclient import TestClient

OS_URL = os.environ.get("OPENSEARCH_URL", "http://127.0.0.1:9200")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")

INDEX = "narralytica-segments-v1"
COLLECTION = "narralytica-segments-v1"

VID = "video_01"
SID1 = "seg_01"
SID2 = "seg_02"


def seed_opensearch(
    *,
    created_at_1: str = "2026-01-01T00:00:00Z",
    created_at_2: str = "2026-01-02T00:00:00Z",
):
    c = httpx.Client(timeout=10)

    # Create index if needed
    c.put(
        f"{OS_URL}/{INDEX}",
        json={
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": {
                "properties": {
                    "segment_id": {"type": "keyword"},
                    "video_id": {"type": "keyword"},
                    "text": {"type": "text"},
                    "language": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "created_at": {"type": "date"},
                }
            },
        },
    )

    # Index docs
    c.post(
        f"{OS_URL}/{INDEX}/_doc/{SID1}",
        json={
            "segment_id": SID1,
            "video_id": VID,
            "text": "hello world",
            "language": "en",
            "source": "whisper",
            "created_at": created_at_1,
        },
    ).raise_for_status()

    c.post(
        f"{OS_URL}/{INDEX}/_doc/{SID2}",
        json={
            "segment_id": SID2,
            "video_id": VID,
            "text": "bonjour le monde",
            "language": "fr",
            "source": "whisper",
            "created_at": created_at_2,
        },
    ).raise_for_status()

    c.post(f"{OS_URL}/{INDEX}/_refresh").raise_for_status()


def seed_qdrant():
    c = httpx.Client(timeout=10)

    # Create collection (409 if exists is OK)
    r = c.put(
        f"{QDRANT_URL}/collections/{COLLECTION}",
        json={"vectors": {"size": 1024, "distance": "Cosine"}},
        timeout=10,
    )
    if r.status_code not in (200, 201, 409):
        r.raise_for_status()

    # Qdrant point IDs must be UUID or unsigned int.
    # Use stable UUIDv5 derived from segment_id.
    points = [
        {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, SID1)),
            "vector": [0.0] * 1024,
            "payload": {"segment_id": SID1},
        },
        {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, SID2)),
            "vector": [0.0] * 1024,
            "payload": {"segment_id": SID2},
        },
    ]

    c.put(
        f"{QDRANT_URL}/collections/{COLLECTION}/points?wait=true",
        json={"points": points},
        timeout=10,
    ).raise_for_status()


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

    return TestClient(app)


def test_keyword_hit():
    seed_opensearch()
    seed_qdrant()

    c = client()
    r = c.post("/api/v1/search", json={"query": "hello", "semantic": False})

    assert r.status_code == 200
    ids = [i["segment_id"] for i in r.json()["items"]]
    assert SID1 in ids


def test_filter_language():
    seed_opensearch()
    seed_qdrant()

    c = client()
    r = c.post(
        "/api/v1/search",
        json={"query": "", "filters": {"language": "fr"}, "semantic": False},
    )

    assert r.status_code == 200
    ids = [i["segment_id"] for i in r.json()["items"]]
    assert SID2 in ids
    assert SID1 not in ids


def test_filter_date_narrows():
    seed_opensearch(
        created_at_1="2026-01-01T00:00:00Z",
        created_at_2="2026-01-10T00:00:00Z",
    )
    seed_qdrant()

    c = client()
    r = c.post(
        "/api/v1/search",
        json={
            "query": "",
            "filters": {"date_from": "2026-01-05T00:00:00Z"},
            "semantic": False,
        },
    )

    assert r.status_code == 200
    ids = [i["segment_id"] for i in r.json()["items"]]
    assert SID2 in ids
    assert SID1 not in ids


def test_merge_no_duplicates(monkeypatch):
    seed_opensearch()
    seed_qdrant()

    c = client()

    class _VHit:
        def __init__(self, segment_id: str, score: float):
            self.segment_id = segment_id
            self.score = score

    def fake_vector_search(*, query_text: str, filters: dict, top_k: int):
        return [_VHit(SID1, 0.99), _VHit(SID2, 0.98)]

    import services.api.src.routes.search as search_routes

    monkeypatch.setattr(search_routes, "vector_search", fake_vector_search)

    r = c.post("/api/v1/search", json={"query": "hello", "semantic": True})

    assert r.status_code == 200
    ids = [i["segment_id"] for i in r.json()["items"]]
    assert len(ids) == len(set(ids))


def test_vector_search_no_crash():
    seed_opensearch()
    seed_qdrant()

    c = client()
    r = c.post("/api/v1/search", json={"query": "hello", "semantic": False})
    assert r.status_code == 200
