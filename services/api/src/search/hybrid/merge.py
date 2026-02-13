from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from packages.search.ranking import MergeWeights, merge_ranked_ids


@dataclass(frozen=True)
class HybridItem:
    segment_id: str
    score: float
    lexical_rank: int | None
    vector_rank: int | None


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

    weights = MergeWeights(
        lexical=float(weight_lexical),
        vector=float(weight_vector),
    )

    merged = merge_ranked_ids(
        lexical_ids=lex_ids,
        vector_ids=vec_ids,
        weights=weights,
    )

    out: list[HybridItem] = []
    for x in merged:
        out.append(
            HybridItem(
                segment_id=x.segment_id,
                score=float(x.score),
                lexical_rank=x.lexical_rank,
                vector_rank=x.vector_rank,
            )
        )
    return out
