from typing import Any

from fastapi.testclient import TestClient


def _make_client() -> TestClient:
    from services.api.src.main import create_app

    app = create_app()

    # Override auth for tests.
    import services.api.src.auth.deps as auth_deps

    def _fake_require_api_key() -> dict[str, Any]:
        return {"api_key_id": "k_test", "name": "tests", "scopes": None}

    app.dependency_overrides[auth_deps.require_api_key] = _fake_require_api_key

    # Override DB dependency: this test must not require DATABASE_URL.
    import services.api.src.services.db as db_deps

    def _fake_db():
        yield None

    app.dependency_overrides[db_deps.get_db] = _fake_db

    return TestClient(app, raise_server_exceptions=True)


def test_search_response_is_stably_sorted(monkeypatch):
    client = _make_client()

    import services.api.src.routes.search as search_module

    # Two segments with same combined score to exercise tie-break.
    def fake_opensearch_search(body):
        lexical = [
            {"segment_id": "seg_b", "score": 1.0},
            {"segment_id": "seg_a", "score": 1.0},
        ]
        sources = {
            "seg_a": {
                "video_id": "vid_01",
                "start_ms": 2000,
                "end_ms": 3000,
                "text": "A",
            },
            "seg_b": {
                "video_id": "vid_01",
                "start_ms": 1000,
                "end_ms": 2000,
                "text": "B",
            },
        }
        lexical_scores = {"seg_a": 1.0, "seg_b": 1.0}

        # highlights with shuffled keys to ensure deterministic output ordering
        highlights = {
            "seg_a": [{"field": "text", "text": "x"}],
            "seg_b": [{"field": "text", "text": "y"}],
        }
        return lexical, sources, lexical_scores, highlights

    def fake_mget(ids):
        return {}

    def fake_vector_search(*args, **kwargs):
        return []

    monkeypatch.setattr(search_module, "_opensearch_search", fake_opensearch_search)
    monkeypatch.setattr(search_module, "_opensearch_mget", fake_mget)
    monkeypatch.setattr(search_module, "vector_search", fake_vector_search)

    resp = client.post(
        "/api/v1/search",
        json={"query": "hello", "mode": "lexical", "limit": 10, "offset": 0},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Expect seg_b first because same score, same video_id, but earlier start_ms
    ids = [it["segment"]["id"] for it in data["items"]]
    assert ids == ["seg_b", "seg_a"]
