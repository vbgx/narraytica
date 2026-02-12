from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient
from services.api.src.main import create_app


def _make_client():
    app = create_app()

    # Override auth for tests: we test ingest semantics separately from auth.
    import services.api.src.auth.deps as auth_deps

    def _fake_require_api_key() -> dict[str, Any]:
        return {"api_key_id": "k_test", "name": "tests", "scopes": None}

    app.dependency_overrides[auth_deps.require_api_key] = _fake_require_api_key
    return TestClient(app)


def test_ingest_valid_returns_ids():
    c = _make_client()

    payload = {
        "external_id": "ext_valid_001",
        "source": {"kind": "external_url", "url": "https://example.com/video.mp4"},
    }

    r = c.post("/api/v1/ingest", json=payload)
    assert r.status_code in (200, 201), r.text

    body = r.json()
    # Be tolerant: depending on implementation you may return job_id/video_id.
    assert isinstance(body, dict)
    assert any(k in body for k in ("job_id", "video_id", "ingest_id", "id")), body


def test_ingest_invalid_400():
    c = _make_client()

    # Missing required URL in source
    r = c.post("/api/v1/ingest", json={"source": {"kind": "external_url"}})
    assert r.status_code == 400, r.text


def test_ingest_idempotent_external_id():
    c = _make_client()

    payload = {
        "external_id": "ext_123",
        "source": {"kind": "external_url", "url": "https://example.com/video.mp4"},
    }

    r1 = c.post("/api/v1/ingest", json=payload)
    assert r1.status_code in (200, 201), r1.text

    r2 = c.post("/api/v1/ingest", json=payload)

    # Idempotency may return 200 or 201, but must not create duplicates.
    assert r2.status_code in (200, 201), r2.text

    # If response includes an ID, it should be stable across calls.
    b1, b2 = r1.json(), r2.json()
    for key in ("job_id", "video_id", "ingest_id", "id"):
        if key in b1 and key in b2:
            assert b1[key] == b2[key]
            break
