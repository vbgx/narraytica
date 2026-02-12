from __future__ import annotations

import os
import time
from collections.abc import Iterator

import pytest
import requests


def _env(name: str, default: str) -> str:
    return (os.environ.get(name) or default).strip().rstrip("/")


@pytest.fixture(scope="session")
def opensearch_url() -> str:
    return _env("OPENSEARCH_URL", "http://localhost:9200")


@pytest.fixture(scope="session")
def qdrant_url() -> str:
    return _env("QDRANT_URL", "http://localhost:6333")


def _wait_http_ok(url: str, timeout_s: float = 20.0) -> None:
    deadline = time.time() + timeout_s
    last_err: str | None = None
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if 200 <= r.status_code < 500:
                return
            last_err = f"status={r.status_code}"
        except Exception as e:
            last_err = str(e)
        time.sleep(0.5)
    raise RuntimeError(f"service not ready: {url} ({last_err})")


@pytest.fixture(scope="session", autouse=True)
def require_search_services(opensearch_url: str, qdrant_url: str) -> Iterator[None]:
    try:
        _wait_http_ok(f"{opensearch_url}/_cluster/health")
        _wait_http_ok(f"{qdrant_url}/collections")
    except Exception as e:
        pytest.skip(f"opensearch/qdrant not reachable: {e}")
    yield
