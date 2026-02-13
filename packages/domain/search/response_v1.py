from __future__ import annotations

from typing import Any


def stable_sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def k(it: dict[str, Any]) -> tuple:
        seg = it["segment"]
        score = it["score"]

        return (
            -float(score["combined"]),
            str(seg["video_id"]),
            int(seg["start_ms"]),
            str(seg["id"]),
        )

    return sorted(items, key=k)


def build_search_response_v1(
    *,
    items: list[dict[str, Any]],
    limit: int,
    offset: int,
    total: int | None,
) -> dict[str, Any]:

    out_items: list[dict[str, Any]] = []

    for it in items:
        seg = it["segment"]
        score = it["score"]
        hl = it.get("highlights")

        if hl:
            hl = [
                {
                    "field": h["field"],
                    "text": h["text"],
                }
                for h in hl
            ]
        else:
            hl = []

        out_items.append(
            {
                "segment": {
                    "id": str(seg["id"]),
                    "video_id": str(seg["video_id"]),
                    "start_ms": int(seg["start_ms"]),
                    "end_ms": int(seg["end_ms"]),
                    "text": str(seg["text"]),
                },
                "score": {
                    "combined": float(score["combined"]),
                },
                "highlights": hl,
            }
        )

    out_items = stable_sort_items(out_items)

    page = {
        "limit": int(limit),
        "offset": int(offset),
        "total": total if total is None else int(total),
    }

    return {
        "items": out_items,
        "page": page,
    }
