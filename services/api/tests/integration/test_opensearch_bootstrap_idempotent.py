from __future__ import annotations

import importlib
import os
import uuid

import pytest
import requests

pytestmark = pytest.mark.opensearch_integration


def _auth():
    user = os.environ.get("OPENSEARCH_USERNAME") or "admin"
    pwd = os.environ.get("OPENSEARCH_PASSWORD") or "LocalDevOnly_ChangeMe_123!"
    return (user, pwd)


def test_opensearch_bootstrap_idempotent(monkeypatch):
    """
    OpenSearch integration test:
    - calls bootstrap_opensearch() twice
    - asserts the target index exists after
    """
    # Allow CI to inject OPENSEARCH_URL. Keep a safe local default.
    os.environ.setdefault("OPENSEARCH_URL", "http://127.0.0.1:9200")
    os.environ.setdefault("OPENSEARCH_USERNAME", "admin")
    os.environ.setdefault("OPENSEARCH_PASSWORD", "LocalDevOnly_ChangeMe_123!")

    # Pick a unique index name for this test run
    index_name = f"narralytica-it-bootstrap-videos-{uuid.uuid4().hex[:8]}"

    # We want bootstrap enabled and deterministic timeouts
    os.environ["OPENSEARCH_BOOTSTRAP_ENABLED"] = "true"
    os.environ["OPENSEARCH_TIMEOUT_SECONDS"] = "10"

    # The bootstrap uses these settings keys
    os.environ["OPENSEARCH_VIDEOS_INDEX"] = index_name
    os.environ["OPENSEARCH_VIDEOS_TEMPLATE_NAME"] = "narralytica-it-videos-template"

    # Reload settings + bootstrap module so env is applied
    import services.api.src.config as cfg
    import services.api.src.search.opensearch.bootstrap as bs

    importlib.reload(cfg)
    importlib.reload(bs)

    base = os.environ["OPENSEARCH_URL"].rstrip("/")
    auth = _auth()

    # Clean up any prior index from earlier runs (best-effort)
    requests.delete(f"{base}/{index_name}", auth=auth, timeout=10)

    # Call twice: must be idempotent
    bs.bootstrap_opensearch()
    bs.bootstrap_opensearch()

    # Assert index exists
    r = requests.head(f"{base}/{index_name}", auth=auth, timeout=10)
    assert r.status_code == 200
