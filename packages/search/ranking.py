from __future__ import annotations

from dataclasses import dataclass

from .ports import LexicalResult, VectorResult
from .types import SearchItem, SearchScore


@dataclass(frozen=True)
class MergeWeights:
    lexical: float = 0.5
    vector: float = 0.5


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
