from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .types import SearchItem, SearchScore


@dataclass(frozen=True)
class MergeWeights:
    lexical: float = 0.5
    vector: float = 0.5


def merge_hybrid_items(
    lexical_items: Iterable[SearchItem],
    semantic_items: Iterable[SearchItem],
    *,
    weights: MergeWeights | None = None,
) -> list[SearchItem]:
    """
    Deterministic hybrid merge at the item level.

    Rules:
    - Dedup by segment.id
    - combined = wL*lex + wV*vec (missing = 0)
    - Stable tie-break: combined desc, then segment.id asc
    """
    if weights is None:
        weights = MergeWeights()

    by_seg: dict[str, tuple[float | None, float | None, SearchItem]] = {}

    def _take(
        item: SearchItem,
        *,
        lexical: float | None,
        vector: float | None,
    ) -> None:
        sid = item.segment.id
        prev = by_seg.get(sid)
        if prev is None:
            by_seg[sid] = (lexical, vector, item)
            return

        pl, pv, base = prev
        nl = lexical if lexical is not None else pl
        nv = vector if vector is not None else pv
        by_seg[sid] = (nl, nv, base)

    for it in lexical_items:
        _take(
            it,
            lexical=(
                it.score.lexical if it.score.lexical is not None else it.score.combined
            ),
            vector=None,
        )

    for it in semantic_items:
        _take(
            it,
            lexical=None,
            vector=(
                it.score.vector if it.score.vector is not None else it.score.combined
            ),
        )

    merged: list[SearchItem] = []

    for _sid, (lex, vec, base) in by_seg.items():
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
                    lexical_rank=base.score.lexical_rank,
                    vector_rank=base.score.vector_rank,
                ),
            )
        )

    merged.sort(key=lambda it: (-it.score.combined, it.segment.id))
    return merged
