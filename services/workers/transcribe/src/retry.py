from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from asr.errors import (
    ASR_ERR_AUDIO_DOWNLOAD_FAILED,
    ASR_ERR_PROVIDER_UNAVAILABLE,
    ASR_ERR_TRANSCRIPTION_FAILED,
    ASR_ERR_TRANSCRIPTION_TIMEOUT,
    AsrError,
)


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int
    backoff_base_s: float
    backoff_max_s: float
    job_timeout_s: float
    attempt_timeout_s: float


def _now_s() -> float:
    return time.monotonic()


def is_retryable_asr_error(e: AsrError) -> bool:
    # Retry only transient-ish failure classes.
    return e.code in {
        ASR_ERR_PROVIDER_UNAVAILABLE,
        ASR_ERR_AUDIO_DOWNLOAD_FAILED,
        ASR_ERR_TRANSCRIPTION_FAILED,
        ASR_ERR_TRANSCRIPTION_TIMEOUT,
    }


def run_with_retry[T](
    fn: Callable[[float], T],
    *,
    cfg: RetryConfig,
    on_attempt: Callable[[int, float], None] | None = None,
    on_error: Callable[[int, float, Exception], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """
    fn(attempt_timeout_s) -> result
    Deterministic backoff (no jitter).
    Enforces global job deadline and per-attempt timeout budget.
    """
    start = _now_s()
    deadline = start + max(0.0, cfg.job_timeout_s)

    last_err: Exception | None = None

    for attempt in range(1, cfg.max_attempts + 1):
        now = _now_s()
        remaining = deadline - now
        if remaining <= 0:
            raise AsrError("asr_job_timeout", f"job_timeout_s={cfg.job_timeout_s}")

        attempt_timeout = min(cfg.attempt_timeout_s, remaining)
        if on_attempt:
            on_attempt(attempt, attempt_timeout)

        try:
            return fn(attempt_timeout)
        except AsrError as e:
            last_err = e
            if on_error:
                on_error(attempt, attempt_timeout, e)

            if attempt >= cfg.max_attempts or not is_retryable_asr_error(e):
                raise

            # deterministic exponential backoff: base * 2^(attempt-1)
            backoff = cfg.backoff_base_s * (2 ** (attempt - 1))
            if backoff > cfg.backoff_max_s:
                backoff = cfg.backoff_max_s

            # don't sleep past deadline
            now2 = _now_s()
            remaining2 = deadline - now2
            if remaining2 <= 0:
                raise AsrError(
                    "asr_job_timeout",
                    f"job_timeout_s={cfg.job_timeout_s}",
                ) from e

            sleep(min(backoff, remaining2))
        except Exception as e:
            last_err = e
            if on_error:
                on_error(attempt, attempt_timeout, e)
            raise

    # unreachable, but keeps type checkers happy
    assert last_err is not None
    raise last_err
