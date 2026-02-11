import json
import logging
import os
import signal
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


# -----------------------------
# Settings (env-driven)
# -----------------------------
WORKER_NAME = os.getenv("WORKER_NAME", "worker-template")
LOG_LEVEL = os.getenv("WORKER_LOG_LEVEL", "info").lower()
POLL_INTERVAL_S = float(os.getenv("WORKER_POLL_INTERVAL_S", "1.0"))


# -----------------------------
# Structured JSON logging
# -----------------------------
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
            "worker": WORKER_NAME,
        }

        for key in ("job_id", "job_type", "status", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(LOG_LEVEL.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


log = logging.getLogger("worker")


# -----------------------------
# Job model + example handler
# -----------------------------
@dataclass(frozen=True)
class Job:
    job_id: str
    job_type: str
    payload: Dict[str, Any]


def example_handler(job: Job) -> Dict[str, Any]:
    name = str(job.payload.get("name", "world"))
    return {"message": f"hello {name}"}


# -----------------------------
# Runner
# -----------------------------
_shutdown = False


def _handle_shutdown(signum, frame) -> None:
    global _shutdown
    _shutdown = True


def poll_once() -> list[Job]:
    """
    Template-only polling.
    Emits one example job on first run, then none.
    Replace this with queue polling / DB leasing / event consumption.
    """
    if not hasattr(poll_once, "_did_emit"):
        poll_once._did_emit = True  # type: ignore[attr-defined]
        return [Job(job_id=str(uuid.uuid4()), job_type="example", payload={"name": "narralytica"})]
    return []


def process_job(job: Job) -> None:
    start = time.perf_counter()
    log.info("job_received", extra={"job_id": job.job_id, "job_type": job.job_type, "status": "received"})

    try:
        if job.job_type != "example":
            log.warning("job_unhandled", extra={"job_id": job.job_id, "job_type": job.job_type, "status": "skipped"})
            return

        _ = example_handler(job)
        duration_ms = int((time.perf_counter() - start) * 1000)
        log.info(
            "job_succeeded",
            extra={"job_id": job.job_id, "job_type": job.job_type, "status": "succeeded", "duration_ms": duration_ms},
        )
    except Exception:
        duration_ms = int((time.perf_counter() - start) * 1000)
        log.exception(
            "job_failed",
            extra={"job_id": job.job_id, "job_type": job.job_type, "status": "failed", "duration_ms": duration_ms},
        )


def main() -> None:
    setup_logging()

    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    log.info("worker_starting", extra={"status": "starting"})

    try:
        while not _shutdown:
            jobs = poll_once()
            if not jobs:
                time.sleep(POLL_INTERVAL_S)
                continue

            for job in jobs:
                process_job(job)

    finally:
        log.info("worker_stopped", extra={"status": "stopped"})


if __name__ == "__main__":
    main()
