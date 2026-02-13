from __future__ import annotations

import os

import requests


def _auth():
    user = os.environ.get("OPENSEARCH_USERNAME")
    pwd = os.environ.get("OPENSEARCH_PASSWORD")
    if user and pwd:
        return (user, pwd)
    return None


def bootstrap_opensearch() -> None:
    """
    Idempotent OpenSearch bootstrap used by integration tests.

    - If OPENSEARCH_BOOTSTRAP_ENABLED != "true" → no-op
    - Ensures target index exists
    - Safe to call multiple times
    """

    if os.environ.get("OPENSEARCH_BOOTSTRAP_ENABLED") != "true":
        return

    base = os.environ.get("OPENSEARCH_URL")
    index = os.environ.get("OPENSEARCH_VIDEOS_INDEX")

    if not base or not index:
        return

    base = base.rstrip("/")
    auth = _auth()

    # Check if index exists
    r = requests.head(f"{base}/{index}", auth=auth, timeout=10)

    if r.status_code == 404:
        # Create empty index
        requests.put(
            f"{base}/{index}",
            json={},
            auth=auth,
            timeout=10,
        )
