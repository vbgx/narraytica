import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("ingest-worker")


@dataclass(frozen=True)
class JobCtx:
    job_id: str
    video_id: str


def _base(ctx: JobCtx, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"job_id": ctx.job_id, "video_id": ctx.video_id}
    out.update(extra)
    return out


def log_event(ctx: JobCtx, event: str, **extra: Any) -> None:
    logger.info(event, extra=_base(ctx, **extra))


def log_error(ctx: JobCtx, event: str, err: BaseException, **extra: Any) -> None:
    """
    Logs an error with full stacktrace (via logger.exception).
    Use this inside an exception handler (except ...) to preserve context.
    """
    logger.exception(
        event,
        extra=_base(
            ctx,
            error_type=type(err).__name__,
            error=str(err),
            **extra,
        ),
    )


@contextmanager
def timed_phase(ctx: JobCtx, phase: str, **extra: Any):
    """
    Context manager that logs phase start/end and emits a duration metric.
    """
    start = time.perf_counter()
    log_event(ctx, "phase_start", phase=phase, **extra)
    try:
        yield
    except Exception as e:
        dur_ms = int((time.perf_counter() - start) * 1000)
        log_error(ctx, "phase_failed", e, phase=phase, duration_ms=dur_ms, **extra)
        raise
    else:
        dur_ms = int((time.perf_counter() - start) * 1000)
        log_event(ctx, "phase_complete", phase=phase, duration_ms=dur_ms, **extra)


def emit_metric(name: str, value: float, labels: dict[str, str] | None = None) -> None:
    """
    Minimal metrics emitter (log-based).
    Later: wire to Prometheus/OTel metrics. For now, we keep it observable via logs.
    """
    labels = labels or {}
    logger.info(
        "metric",
        extra={"metric_name": name, "metric_value": value, "labels": labels},
    )
