from __future__ import annotations

import importlib
import os
from datetime import UTC, datetime

import requests
from fastapi.testclient import TestClient

INDEX = "narralytica-it-segments"
COLLECTION = "narralytica-it-segments"

SID1 = "00000000-0000-0000-0000-000000000001"
SID2 = "00000000-0000-0000-0000-000000000002"


def setup_module():
    os.environ["OPENSEARCH_URL"] = "http://localhost:9200"
    os.environ["OPENSEARCH_USERNAME"] = "admin"
    os.environ["OPENSEARCH_PASSWORD"] = "LocalDevOnly_ChangeMe_123!"
    os.environ["OPENSEARCH_SEGMENTS_INDEX"] = INDEX

    os.environ["QDRANT_URL"] = "http://localhost:6333"
    os.environ["QDRANT_SEGMENTS_COLLECTION"] = COLLECTION

    os.environ["EMBEDDING_VECTOR_SIZE"] = "1024"
    os.environ["EMBEDDINGS_URL"] = ""


def _auth():
    return (
        os.environ["OPENSEARCH_USERNAME"],
        os.environ["OPENSEARCH_PASSWORD"],
    )


def seed_opensearch(
    *, created_at_1: str | None = None, created_at_2: str | None = None
):
    base = os.environ["OPENSEARCH_URL"].rstrip("/")
    auth = _auth()

    requests.delete(f"{base}/{INDEX}", auth=auth, timeout=10)

    index_body = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            }
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "segment_id": {"type": "keyword"},
                "video_id": {"type": "keyword"},
                "speaker_id": {"type": "keyword"},
                "language": {"type": "keyword"},
                "source": {"type": "keyword"},
                "created_at": {"type": "date"},
                "text": {
                    "type": "text",
                    "fields": {"prefix": {"type": "search_as_you_type"}},
                },
            },
        },
    }

    requests.put(
        f"{base}/{INDEX}",
        json=index_body,
        auth=auth,
        timeout=10,
    ).raise_for_status()

    now = datetime.now(UTC).isoformat()
    a1 = created_at_1 or now
    a2 = created_at_2 or now

    docs = [
        {
            "id": SID1,
            "segment_id": SID1,
            "video_id": "v1",
            "speaker_id": "spk1",
            "language": "en",
            "source": "youtube",
            "text": "hello world from narralytica",
            "created_at": a1,
        },
        {
            "id": SID2,
            "segment_id": SID2,
            "video_id": "v1",
            "speaker_id": "spk2",
            "language": "fr",
            "source": "youtube",
            "text": "bonjour le monde",
            "created_at": a2,
        },
    ]

    for d in docs:
        requests.put(
            f"{base}/{INDEX}/_doc/{d['id']}",
            json=d,
            auth=auth,
            timeout=10,
        ).raise_for_status()

    requests.post(f"{base}/{INDEX}/_refresh", auth=auth, timeout=10).raise_for_status()


def seed_qdrant():
    base = os.environ["QDRANT_URL"]

    requests.delete(f"{base}/collections/{COLLECTION}", timeout=10)
    requests.put(
        f"{base}/collections/{COLLECTION}",
        json={"vectors": {"size": 1024, "distance": "Cosine"}},
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
    return TestClient(app)


def test_keyword_hit():
    seed_opensearch()
    seed_qdrant()

    c = client()
    r = c.post("/search", json={"query": "hello", "semantic": False})

    assert r.status_code == 200
    ids = [i["segment_id"] for i in r.json()["items"]]
    assert SID1 in ids


def test_filter_language():
    seed_opensearch()
    seed_qdrant()

    c = client()
    r = c.post(
        "/search",
        json={"query": "", "filters": {"language": "fr"}, "semantic": False},
    )

    assert r.status_code == 200
    ids = [i["segment_id"] for i in r.json()["items"]]
    assert ids == [SID2]


def test_filter_date_narrows():
    seed_opensearch(
        created_at_1="2026-01-01T00:00:00Z",
        created_at_2="2026-01-10T00:00:00Z",
    )
    seed_qdrant()

    c = client()
    r = c.post(
        "/search",
        json={
            "query": "",
            "filters": {"date_from": "2026-01-05T00:00:00Z"},
            "semantic": False,
        },
    )

    assert r.status_code == 200
    ids = [i["segment_id"] for i in r.json()["items"]]
    assert ids == [SID2]


def test_merge_no_duplicates(monkeypatch):
    seed_opensearch()
    seed_qdrant()

    # IMPORTANT: client() reloads modules, so build it BEFORE monkeypatching.
    c = client()

    class _VHit:
        def __init__(self, segment_id: str, score: float):
            self.segment_id = segment_id
            self.score = score

    def fake_vector_search(*, query_text: str, filters: dict, top_k: int):
        return [_VHit(SID1, 0.99), _VHit(SID2, 0.98)]

    import services.api.src.routes.search as search_routes

    monkeypatch.setattr(search_routes, "vector_search", fake_vector_search)

    r = c.post("/search", json={"query": "hello", "semantic": True})

    assert r.status_code == 200
    ids = [i["segment_id"] for i in r.json()["items"]]

    assert len(ids) == len(set(ids))
    assert SID1 in ids
    assert SID2 in ids


def test_vector_search_no_crash():
    seed_opensearch()
    seed_qdrant()

    c = client()
    r = c.post("/search", json={"query": "hello", "semantic": False})
    assert r.status_code == 200
