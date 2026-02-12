from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True, scope="session")
def _test_env_defaults() -> None:
    """
    Ensure tests and API route code share the same OpenSearch/Qdrant config.
    We intentionally fail fast in app code if these are missing.
    """
    os.environ.setdefault("OPENSEARCH_URL", "http://localhost:9200")
    os.environ.setdefault("OPENSEARCH_SEGMENTS_INDEX", "narralytica-segments-v1")

    # If your vector search path needs it (harmless if unused):
    os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
    os.environ.setdefault("QDRANT_SEGMENTS_COLLECTION", "narralytica-segments-v1")
