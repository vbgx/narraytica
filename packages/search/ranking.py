from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .ports import LexicalResult, VectorResult
from .types import SearchItem, SearchScore


@dataclass(frozen=True)
class MergeWeights:
    lexical: float = 0.5
    vector: float = 0.5


# ============================================================================
# V1: ID-only deterministic hybrid merge (used by services/api + application v1)
# - PURE (no HTTP, no backends)
# - No dict/Any in signature (anti-drift)
# - Score is rank-normalized (not backend score), matches prior behavior
# ============================================================================


@dataclass(frozen=True)
class HybridRankedId:
    segment_id: str
    score: float
    lexical_rank: int | None
    vector_rank: int | None


def _rank_scores(ids: Sequence[str]) -> dict[str, float]:
    n = len(ids)
    if n == 0:
        return {}
    out: dict[str, float] = {}
    for i, sid in enumerate(ids):
        rank = i + 1
        out[str(sid)] = (n - (rank - 1)) / n
    return out


def merge_ranked_ids(
    *,
    lexical_ids: Sequence[str] | None,
    vector_ids: Sequence[str] | None,
    weights: MergeWeights | None = None,
) -> list[HybridRankedId]:
    if weights is None:
        weights = MergeWeights()

    lex_ids = [str(x) for x in (lexical_ids or []) if x is not None]
    vec_ids = [str(x) for x in (vector_ids or []) if x is not None]

    lex_norm = _rank_scores(lex_ids)
    vec_norm = _rank_scores(vec_ids)

    union_ids = set(lex_ids) | set(vec_ids)

    lex_rank_pos = {sid: i + 1 for i, sid in enumerate(lex_ids)}
    vec_rank_pos = {sid: i + 1 for i, sid in enumerate(vec_ids)}

    merged: list[HybridRankedId] = []
    for sid in union_ids:
        s = (weights.lexical * lex_norm.get(sid, 0.0)) + (
            weights.vector * vec_norm.get(sid, 0.0)
        )
        merged.append(
            HybridRankedId(
                segment_id=sid,
                score=float(s),
                lexical_rank=lex_rank_pos.get(sid),
                vector_rank=vec_rank_pos.get(sid),
            )
        )

    merged.sort(key=lambda x: (-x.score, x.segment_id))
    return merged


# ============================================================================
# V2+: Typed merge for SearchEngine (domain-first)
# ============================================================================


def merge_hybrid(
    *,
    lexical: LexicalResult,
    vector: VectorResult,
    weights: MergeWeights | None = None,
) -> list[SearchItem]:
    if weights is None:
        weights = MergeWeights()

    by_id: dict[
        str,
        tuple[
            float | None,
            float | None,
            SearchItem,
            int | None,
            int | None,
        ],
    ] = {}

    def take_from_lex(h) -> None:
        sid = h.item.segment.id
        prev = by_id.get(sid)
        if prev is None:
            by_id[sid] = (h.score_lexical, None, h.item, h.lexical_rank, None)
            return

        lex, vec, base, lr, vr = prev
        by_id[sid] = (
            h.score_lexical if lex is None else lex,
            vec,
            base,
            lr or h.lexical_rank,
            vr,
        )

    def take_from_vec(h) -> None:
        sid = h.item.segment.id
        prev = by_id.get(sid)
        if prev is None:
            by_id[sid] = (None, h.score_vector, h.item, None, h.vector_rank)
            return

        lex, vec, base, lr, vr = prev
        by_id[sid] = (
            lex,
            h.score_vector if vec is None else vec,
            base,
            lr,
            vr or h.vector_rank,
        )

    for h in lexical.hits:
        take_from_lex(h)

    for h in vector.hits:
        take_from_vec(h)

    merged: list[SearchItem] = []

    for _sid, (lex, vec, base, lr, vr) in by_id.items():
        lex_v = float(lex or 0.0)
        vec_v = float(vec or 0.0)
        combined = (weights.lexical * lex_v) + (weights.vector * vec_v)

        merged.append(
            SearchItem(
                segment=base.segment,
                video=base.video,
                speaker=base.speaker,
                highlights=base.highlights,
                score=SearchScore(
                    combined=float(combined),
                    lexical=float(lex_v) if lex is not None else None,
                    vector=float(vec_v) if vec is not None else None,
                    lexical_rank=lr,
                    vector_rank=vr,
                ),
            )
        )

    merged.sort(key=lambda it: (-it.score.combined, it.segment.id))
    return merged
