from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests

from .embeddings_client import EmbeddingsNotConfiguredError, embed_text
from .filters import build_qdrant_filter

MAX_TOP_K = 50
DEFAULT_TOP_K = 10


class VectorSearchError(RuntimeError):
    pass


@dataclass(frozen=True)
class VectorHit:
    segment_id: str
    score: float


def clamp_top_k(top_k: int | None) -> int:
    if top_k is None:
        return DEFAULT_TOP_K
    return max(1, min(int(top_k), MAX_TOP_K))


def vector_search(
    *,
    query_text: str,
    filters: dict | None,
    top_k: int | None,
) -> list[VectorHit]:
    qdrant_url = (
        (os.environ.get("QDRANT_URL") or "http://localhost:6333").strip().rstrip("/")
    )
    collection = (
        os.environ.get("QDRANT_SEGMENTS_COLLECTION") or "narralytica-segments-v1"
    ).strip()
    timeout_s = float((os.environ.get("QDRANT_TIMEOUT_S") or "10").strip() or "10")

    k = clamp_top_k(top_k)

    try:
        vector = embed_text(query_text)
    except EmbeddingsNotConfiguredError as e:
        raise VectorSearchError(str(e)) from e
    except Exception as e:
        raise VectorSearchError(f"embeddings error: {e}") from e

    q_filter = build_qdrant_filter(filters)

    body: dict[str, Any] = {
        "vector": vector,
        "limit": k,
        "with_payload": False,
        "with_vector": False,
    }
    if q_filter:
        body["filter"] = q_filter

    try:
        r = requests.post(
            f"{qdrant_url}/collections/{collection}/points/search",
            json=body,
            timeout=timeout_s,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        raise VectorSearchError(f"qdrant query failed: {e}") from e

    data = r.json()
    result = data.get("result")
    if not isinstance(result, list):
        raise VectorSearchError("invalid qdrant response shape")

    out: list[VectorHit] = []
    for item in result:
        if not isinstance(item, dict):
            continue
        sid = item.get("id")
        score = item.get("score")
        if sid is None or score is None:
            continue
        out.append(VectorHit(segment_id=str(sid), score=float(score)))

    return out
