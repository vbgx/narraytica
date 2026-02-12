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


def test_opensearch_bootstrap_idempotent():
    """
    OpenSearch integration test:
    - calls bootstrap_opensearch() twice
    - asserts the target index exists after
    """
    os.environ.setdefault("OPENSEARCH_URL", "http://127.0.0.1:9200")
    os.environ.setdefault("OPENSEARCH_USERNAME", "admin")
    os.environ.setdefault("OPENSEARCH_PASSWORD", "LocalDevOnly_ChangeMe_123!")

    # Unique index per run
    index_name = f"narralytica-it-bootstrap-videos-{uuid.uuid4().hex[:8]}"

    os.environ["OPENSEARCH_BOOTSTRAP_ENABLED"] = "true"
    os.environ["OPENSEARCH_TIMEOUT_SECONDS"] = "10"
    os.environ["OPENSEARCH_VIDEOS_INDEX"] = index_name
    os.environ["OPENSEARCH_VIDEOS_TEMPLATE_NAME"] = "narralytica-it-videos-template"

    import services.api.src.config as cfg
    import services.api.src.search.opensearch.bootstrap as bs

    importlib.reload(cfg)
    importlib.reload(bs)

    base = os.environ["OPENSEARCH_URL"].rstrip("/")
    auth = _auth()

    # best-effort cleanup
    requests.delete(f"{base}/{index_name}", auth=auth, timeout=10)

    bs.bootstrap_opensearch()
    bs.bootstrap_opensearch()

    r = requests.head(f"{base}/{index_name}", auth=auth, timeout=10)
    assert r.status_code == 200
