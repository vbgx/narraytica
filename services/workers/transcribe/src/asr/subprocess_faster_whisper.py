from __future__ import annotations

import argparse
import json
from typing import Any

from faster_whisper import WhisperModel


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-path", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", required=True)
    ap.add_argument("--compute-type", required=True)
    args = ap.parse_args()

    model = WhisperModel(
        args.model,
        device=args.device,
        compute_type=args.compute_type,
    )

    segments_it, info = model.transcribe(args.audio_path)

    segments: list[dict[str, Any]] = []
    full_parts: list[str] = []

    for s in segments_it:
        text = (getattr(s, "text", "") or "").strip()
        if text:
            full_parts.append(text)
        segments.append(
            {
                "start_s": float(getattr(s, "start", 0.0)),
                "end_s": float(getattr(s, "end", 0.0)),
                "text": text,
            }
        )

    raw: dict[str, Any] = {
        "model": args.model,
        "device": args.device,
        "compute_type": args.compute_type,
        "language": getattr(info, "language", None),
        "duration": getattr(info, "duration", None),
    }

    out = {
        "text": " ".join(full_parts).strip(),
        "language": getattr(info, "language", None),
        "segments": segments,
        "raw": raw,
    }

    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
