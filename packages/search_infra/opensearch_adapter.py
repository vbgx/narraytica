from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from packages.search.ports import (
    LexicalHit,
    LexicalResult,
    LexicalSearchPort,
    SearchQueryNormalized,
)
from packages.search.types import (
    SearchHighlight,
    SearchItem,
    SearchScore,
    SearchSegment,
)

from .config import OpenSearchConfig
from .opensearch_query import build_lexical_query_body


def highlight_to_items(h: dict[str, Any]) -> list[SearchHighlight]:
    out: list[SearchHighlight] = []
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
                out.append(SearchHighlight(field=field, text=frag))

    return out


def segment_from_source(sid: str, src: dict[str, Any]) -> SearchSegment:
    return SearchSegment(
        id=str(sid),
        video_id=str(src.get("video_id") or ""),
        start_ms=int(src.get("start_ms") or 0),
        end_ms=int(src.get("end_ms") or 0),
        text=str(src.get("text") or ""),
        transcript_id=src.get("transcript_id"),
        speaker_id=src.get("speaker_id"),
        segment_index=src.get("segment_index"),
        language=src.get("language"),
        source=src.get("source"),
        created_at=src.get("created_at"),
        updated_at=src.get("updated_at"),
    )


@dataclass
class OpenSearchAdapter(LexicalSearchPort):
    cfg: OpenSearchConfig

    def search_lexical(self, q: SearchQueryNormalized) -> LexicalResult:
        top_k = min(100, int(q.offset) + int(q.limit))
        body = build_lexical_query_body(q, top_k=top_k)

        url = f"{self.cfg.url}/{self.cfg.segments_index}/_search"
        try:
            with requests.Session() as session:
                session.trust_env = False
                r = session.post(
                    url,
                    json=body,
                    timeout=float(self.cfg.timeout_s),
                    auth=self.cfg.auth,
                )
            if 400 <= r.status_code < 500:
                raise ValueError(f"OpenSearch query error: {r.text}")
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenSearch unavailable: {e}") from e

        hits = (((data or {}).get("hits") or {}).get("hits")) or []
        out_hits: list[LexicalHit] = []

        for rank, h in enumerate(hits, start=1):
            sid = h.get("_id")
            if not sid:
                continue
            sid = str(sid)

            score = float(h.get("_score") or 0.0)
            src = h.get("_source") if isinstance(h.get("_source"), dict) else None
            if not src:
                continue

            seg = segment_from_source(sid, src)

            hl_raw = h.get("highlight")
            highlights = highlight_to_items(hl_raw) if isinstance(hl_raw, dict) else []

            item = SearchItem(
                segment=seg,
                score=SearchScore(
                    combined=score,
                    lexical=score,
                    vector=None,
                    lexical_rank=rank,
                    vector_rank=None,
                ),
                video=None,
                speaker=None,
                highlights=highlights or None,
            )

            out_hits.append(
                LexicalHit(item=item, score_lexical=score, lexical_rank=rank)
            )

        total = None
        try:
            total_raw = (((data or {}).get("hits") or {}).get("total") or {}).get(
                "value"
            )
            if total_raw is not None:
                total = int(total_raw)
        except Exception:
            total = None

        return LexicalResult(hits=out_hits, total=total)

    def mget_segments(self, ids: list[str]) -> dict[str, dict[str, Any]]:
        if not ids:
            return {}

        url = f"{self.cfg.url}/{self.cfg.segments_index}/_mget"
        try:
            with requests.Session() as session:
                session.trust_env = False
                r = session.post(
                    url,
                    json={"ids": ids},
                    timeout=float(self.cfg.timeout_s),
                    auth=self.cfg.auth,
                )
            if 400 <= r.status_code < 500:
                raise ValueError(f"OpenSearch mget error: {r.text}")
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenSearch unavailable: {e}") from e

        docs = data.get("docs")
        if not isinstance(docs, list):
            return {}

        out: dict[str, dict[str, Any]] = {}
        for d in docs:
            if not isinstance(d, dict):
                continue
            sid = d.get("_id")
            found = d.get("found")
            src = d.get("_source")
            if sid and found and isinstance(src, dict):
                out[str(sid)] = src

        return out
