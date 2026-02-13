from __future__ import annotations

import os
from typing import Any

import requests


def _opensearch_url() -> str:
    url = os.environ.get("OPENSEARCH_URL")
    if not url:
        raise RuntimeError("OpenSearch not configured")
    return url.rstrip("/")


def _segments_index() -> str:
    idx = os.environ.get("OPENSEARCH_SEGMENTS_INDEX")
    if not idx:
        raise RuntimeError("OPENSEARCH_SEGMENTS_INDEX not configured")
    return idx


def _os_auth() -> tuple[str, str] | None:
    user = os.environ.get("OPENSEARCH_USERNAME")
    pwd = os.environ.get("OPENSEARCH_PASSWORD")
    if user and pwd:
        return (user, pwd)
    return None


def search(*, body: dict[str, Any]) -> dict[str, Any]:
    url = f"{_opensearch_url()}/{_segments_index()}/_search"
    auth = _os_auth()
    with requests.Session() as session:
        session.trust_env = False
        r = session.post(url, json=body, timeout=10, auth=auth)
    if 400 <= r.status_code < 500:
        raise ValueError(f"OpenSearch query error: {r.text}")
    r.raise_for_status()
    return r.json()


def mget(*, ids: list[str]) -> dict[str, Any]:
    if not ids:
        return {"docs": []}
    url = f"{_opensearch_url()}/{_segments_index()}/_mget"
    auth = _os_auth()
    with requests.Session() as session:
        session.trust_env = False
        r = session.post(url, json={"ids": ids}, timeout=10, auth=auth)
    if 400 <= r.status_code < 500:
        raise ValueError(f"OpenSearch mget error: {r.text}")
    r.raise_for_status()
    return r.json()
