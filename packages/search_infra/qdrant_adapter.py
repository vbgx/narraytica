from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import requests
from packages.search.ports import (
    SearchQueryNormalized,
    VectorHit,
    VectorResult,
    VectorSearchPort,
)
from packages.search.types import SearchItem, SearchScore

from .config import QdrantConfig
from .opensearch_adapter import OpenSearchAdapter, segment_from_source
from .qdrant_filter import build_qdrant_filter


class VectorSearchError(RuntimeError):
    pass


@dataclass
class QdrantAdapter(VectorSearchPort):
    cfg: QdrantConfig
    segment_store: OpenSearchAdapter
    embed_text: Callable[[str], list[float]]

    def search_vector(self, q: SearchQueryNormalized) -> VectorResult:
        if not q.query:
            return VectorResult(hits=[], total=0)

        top_k = max(1, min(50, int(q.offset) + int(q.limit)))

        try:
            vector = self.embed_text(q.query)
        except Exception as e:
            raise VectorSearchError(f"embeddings error: {e}") from e

        body: dict[str, Any] = {
            "vector": vector,
            "limit": int(top_k),
            "with_payload": False,
            "with_vector": False,
        }

        q_filter = build_qdrant_filter(q.filters)
        if q_filter:
            body["filter"] = q_filter

        try:
            r = requests.post(
                f"{self.cfg.url}/collections/{self.cfg.segments_collection}/points/search",
                json=body,
                timeout=float(self.cfg.timeout_s),
            )
            r.raise_for_status()
        except requests.RequestException as e:
            raise VectorSearchError(f"qdrant query failed: {e}") from e

        data = r.json()
        result = data.get("result")
        if not isinstance(result, list):
            raise VectorSearchError("invalid qdrant response shape")

        ids: list[str] = []
        scores: dict[str, float] = {}

        for item in result:
            if not isinstance(item, dict):
                continue
            sid = item.get("id")
            score = item.get("score")
            if sid is None or score is None:
                continue
            sid_s = str(sid)
            ids.append(sid_s)
            scores[sid_s] = float(score)

        sources = self.segment_store.mget_segments(ids)

        hits: list[VectorHit] = []
        for rank, sid in enumerate(ids, start=1):
            src = sources.get(sid)
            if not src:
                continue

            seg = segment_from_source(sid, src)
            score_v = float(scores.get(sid) or 0.0)

            item2 = SearchItem(
                segment=seg,
                score=SearchScore(
                    combined=score_v,
                    lexical=None,
                    vector=score_v,
                    lexical_rank=None,
                    vector_rank=rank,
                ),
                video=None,
                speaker=None,
                highlights=None,
            )

            hits.append(VectorHit(item=item2, score_vector=score_v, vector_rank=rank))

        return VectorResult(hits=hits, total=None)
