from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger("transcribe-worker")


def _now_s() -> float:
    return time.monotonic()


def emit_job_event(
    *,
    event: str,
    job_id: str,
    video_id: str,
    provider: str | None = None,
    transcript_id: str | None = None,
    attempt: int | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {"event": event, "job_id": job_id, "video_id": video_id}
    if provider:
        payload["provider"] = provider
    if transcript_id:
        payload["transcript_id"] = transcript_id
    if attempt is not None:
        payload["attempt"] = attempt
    if extra:
        payload.update(extra)

    logger.info("job_event", extra=payload)


@contextmanager
def span(
    name: str,
    *,
    job_id: str,
    video_id: str,
    provider: str | None = None,
    transcript_id: str | None = None,
    attempt: int | None = None,
    extra: dict[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    attrs: dict[str, Any] = {"job_id": job_id, "video_id": video_id}
    if provider:
        attrs["provider"] = provider
    if transcript_id:
        attrs["transcript_id"] = transcript_id
    if attempt is not None:
        attrs["attempt"] = attempt
    if extra:
        attrs.update(extra)

    start = _now_s()

    try:
        from opentelemetry import trace  # type: ignore

        tracer = trace.get_tracer("narralytica.transcribe")
        with tracer.start_as_current_span(name) as sp:  # type: ignore
            for k, v in attrs.items():
                try:
                    sp.set_attribute(k, v)  # type: ignore
                except Exception:
                    pass
            yield attrs
            dur_ms = int((_now_s() - start) * 1000)
            try:
                sp.set_attribute("duration_ms", dur_ms)  # type: ignore
            except Exception:
                pass
            return
    except Exception:
        pass

    logger.info("span_start", extra={"span": name, **attrs})
    try:
        yield attrs
        dur_ms = int((_now_s() - start) * 1000)
        logger.info("span_end", extra={"span": name, "duration_ms": dur_ms, **attrs})
    except Exception as e:
        dur_ms = int((_now_s() - start) * 1000)
        logger.exception(
            "span_error",
            extra={"span": name, "duration_ms": dur_ms, "error": str(e), **attrs},
        )
        raise
