from __future__ import annotations

import os
from typing import Any

import requests

from .qdrant.vector_search import VectorSearchError, vector_search

MAX_TIMEOUT_S = 10.0


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


def highlight_to_items(h: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert OpenSearch highlight fragments into contract-shaped highlights.

    Determinism: iterate keys in sorted order.
    """
    out: list[dict[str, Any]] = []
    if not isinstance(h, dict):
        return out

    for k in sorted(h.keys()):
        v = h.get(k)
        if not isinstance(v, list):
            continue

        field = "text"
        if k in ("title", "speaker", "metadata"):
            field = k

        for frag in v:
            if isinstance(frag, str) and frag.strip():
                out.append({"field": field, "text": frag})

    return out


def opensearch_search(
    body: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict],
    dict[str, Any],
    dict[str, list[dict[str, Any]]],
]:
    url = f"{_opensearch_url()}/{_segments_index()}/_search"
    auth = _os_auth()

    try:
        with requests.Session() as session:
            session.trust_env = False
            r = session.post(url, json=body, timeout=MAX_TIMEOUT_S, auth=auth)
        if 400 <= r.status_code < 500:
            raise ValueError(f"OpenSearch query error: {r.text}")
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise RuntimeError(f"OpenSearch unavailable: {e}") from e

    hits = (((data or {}).get("hits") or {}).get("hits")) or []
    lexical: list[dict[str, Any]] = []
    sources: dict[str, dict] = {}
    lexical_scores: dict[str, Any] = {}
    highlights: dict[str, list[dict[str, Any]]] = {}

    for h in hits:
        sid = h.get("_id")
        if not sid:
            continue
        sid = str(sid)

        lexical.append({"segment_id": sid, "score": float(h.get("_score") or 0.0)})

        if "_score" in h:
            lexical_scores[sid] = h.get("_score")

        src = h.get("_source")
        if isinstance(src, dict):
            sources[sid] = src

        hl = h.get("highlight")
        if isinstance(hl, dict):
            items = highlight_to_items(hl)
            if items:
                highlights[sid] = items

    return lexical, sources, lexical_scores, highlights


def opensearch_mget(ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    url = f"{_opensearch_url()}/{_segments_index()}/_mget"
    auth = _os_auth()

    try:
        with requests.Session() as session:
            session.trust_env = False
            r = session.post(url, json={"ids": ids}, timeout=MAX_TIMEOUT_S, auth=auth)
        if 400 <= r.status_code < 500:
            raise ValueError(f"OpenSearch mget error: {r.text}")
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise RuntimeError(f"OpenSearch unavailable: {e}") from e

    docs = data.get("docs")
    if not isinstance(docs, list):
        return {}

    out: dict[str, dict] = {}
    for d in docs:
        if not isinstance(d, dict):
            continue
        sid = d.get("_id")
        found = d.get("found")
        src = d.get("_source")
        if sid and found and isinstance(src, dict):
            out[str(sid)] = src

    return out


def vector_search_safe(
    *,
    query_text: str,
    filters: dict | None,
    top_k: int,
) -> list[dict[str, Any]]:
    """
    Return list[{segment_id, score}] and swallow VectorSearchError (as before).
    """
    try:
        v = vector_search(query_text=query_text, filters=filters, top_k=top_k)
        return [{"segment_id": x.segment_id, "score": x.score} for x in v]
    except VectorSearchError:
        return []
