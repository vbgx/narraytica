from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HybridItem:
    segment_id: str
    score: float
    lexical_rank: int | None
    vector_rank: int | None


def _rank_scores(ids: list[str]) -> dict[str, float]:
    n = len(ids)
    if n == 0:
        return {}
    out: dict[str, float] = {}
    for i, sid in enumerate(ids):
        rank = i + 1
        out[sid] = (n - (rank - 1)) / n
    return out


def merge_results(
    *,
    lexical: list[dict[str, Any]] | None,
    vector: list[dict[str, Any]] | None,
    weight_lexical: float = 0.5,
    weight_vector: float = 0.5,
) -> list[HybridItem]:
    lexical = lexical or []
    vector = vector or []

    lex_ids: list[str] = []
    vec_ids: list[str] = []

    for it in lexical:
        if not isinstance(it, dict):
            continue
        sid = it.get("segment_id") or it.get("id")
        if sid is None:
            continue
        lex_ids.append(str(sid))

    for it in vector:
        if not isinstance(it, dict):
            continue
        sid = it.get("segment_id") or it.get("id")
        if sid is None:
            continue
        vec_ids.append(str(sid))

    lex_norm = _rank_scores(lex_ids)
    vec_norm = _rank_scores(vec_ids)

    union_ids = set(lex_ids) | set(vec_ids)

    lex_rank_pos = {sid: i + 1 for i, sid in enumerate(lex_ids)}
    vec_rank_pos = {sid: i + 1 for i, sid in enumerate(vec_ids)}

    merged: list[HybridItem] = []
    for sid in union_ids:
        s = (weight_lexical * lex_norm.get(sid, 0.0)) + (
            weight_vector * vec_norm.get(sid, 0.0)
        )
        merged.append(
            HybridItem(
                segment_id=sid,
                score=float(s),
                lexical_rank=lex_rank_pos.get(sid),
                vector_rank=vec_rank_pos.get(sid),
            )
        )

    merged.sort(key=lambda x: (-x.score, x.segment_id))
    return merged
