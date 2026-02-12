from __future__ import annotations

from typing import Any


def seconds_to_ms(seconds: float | int | None) -> int:
    if seconds is None:
        return 0
    return int(round(float(seconds) * 1000))


def normalize_segments(raw_segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Input (provider-agnostic):
      Each segment can contain:
        - start_s/end_s (float seconds) OR start/end (float seconds)
        - text (str)

    Output (canonical):
      [
        { "start_ms": int, "end_ms": int, "text": str }
      ]

    Constraints enforced:
      - stable ordering
      - start_ms >= 0
      - start_ms < end_ms
      - non-overlapping segments (start_ms >= prev_end_ms)
    """
    normalized: list[dict[str, Any]] = []

    for idx, seg in enumerate(raw_segments):
        # accept both {start_s,end_s} and {start,end}
        start_s = seg.get("start_s", seg.get("start"))
        end_s = seg.get("end_s", seg.get("end"))

        start = seconds_to_ms(start_s)
        end = seconds_to_ms(end_s)

        if end <= start:
            continue

        text = seg.get("text") or ""
        normalized.append(
            {
                "start_ms": max(0, start),
                "end_ms": max(0, end),
                "text": text,
                "_idx": idx,
            }
        )

    # Stable sort by time, then original index
    normalized.sort(key=lambda x: (x["start_ms"], x["end_ms"], x["_idx"]))

    # Enforce non-overlap and monotonicity
    cleaned: list[dict[str, Any]] = []
    prev_end = 0

    for seg in normalized:
        start = max(seg["start_ms"], prev_end)
        end = seg["end_ms"]

        if end <= start:
            continue

        seg["start_ms"] = start
        seg["end_ms"] = end

        prev_end = end
        cleaned.append(seg)

    for seg in cleaned:
        seg.pop("_idx", None)

    return cleaned
