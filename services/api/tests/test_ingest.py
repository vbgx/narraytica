from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.src.main import create_app


def _client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_ingest_valid_returns_ids():
    from services.api.src.routes import ingest as ingest_routes

    class _Actor:
        api_key_id = "k_test"

    app = create_app()
    app.dependency_overrides[ingest_routes.get_actor] = lambda: _Actor()
    c = TestClient(app)

    r = c.post(
        "/api/v1/ingest",
        json={
            "source": {"kind": "external_url", "url": "https://example.com/video.mp4"},
            "metadata": {"foo": "bar"},
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["job_id"]
    assert body["video_id"]
    assert body["status"] == "queued"
    assert body["payload_version"]


def test_ingest_invalid_400():
    from services.api.src.routes import ingest as ingest_routes

    class _Actor:
        api_key_id = "k_test"

    app = create_app()
    app.dependency_overrides[ingest_routes.get_actor] = lambda: _Actor()
    c = TestClient(app)

    r = c.post("/api/v1/ingest", json={"source": {"kind": "external_url"}})
    assert r.status_code == 400


def test_ingest_idempotent_external_id():
    from services.api.src.routes import ingest as ingest_routes

    class _Actor:
        api_key_id = "k_test"

    app = create_app()
    app.dependency_overrides[ingest_routes.get_actor] = lambda: _Actor()
    c = TestClient(app)

    payload = {
        "external_id": "ext_123",
        "source": {"kind": "external_url", "url": "https://example.com/video.mp4"},
    }

    r1 = c.post("/api/v1/ingest", json=payload)
    assert r1.status_code == 201, r1.text
    b1 = r1.json()

    r2 = c.post("/api/v1/ingest", json=payload)
    assert r2.status_code == 201, r2.text
    b2 = r2.json()

    assert b2["job_id"] == b1["job_id"]
    assert b2["video_id"] == b1["video_id"]
    assert b2["idempotent_replay"] is True
