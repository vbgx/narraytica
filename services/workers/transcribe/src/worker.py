from __future__ import annotations

import logging
import os
import time

from db.jobs import claim_next_transcription_job, mark_job_failed, mark_job_succeeded
from db.transcripts import create_mock_transcript

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
POLL_INTERVAL_MS = int(os.getenv("JOB_POLL_INTERVAL_MS", "1000"))
SLEEP_ON_EMPTY_MS = int(os.getenv("JOB_EMPTY_SLEEP_MS", str(POLL_INTERVAL_MS)))
EXECUTION_MODE = os.getenv("TRANSCRIBE_MODE", "mock")  # mock|real (future)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("transcribe-worker")


def execute_transcription(job: dict) -> None:
    """
    v0 skeleton:
      - mock: write a 'completed' transcript row
      - future: download audio, run ASR provider,
        store artifact, write transcript rows
    """
    job_id = job["id"]
    video_id = job["video_id"]

    if EXECUTION_MODE != "mock":
        raise NotImplementedError("TRANSCRIBE_MODE=real is not implemented yet")

    transcript_id = create_mock_transcript(
        video_id=video_id,
        metadata={"job_id": job_id, "note": "mock transcription"},
    )
    logger.info(
        "transcription_mock_completed",
        extra={"job_id": job_id, "video_id": video_id, "transcript_id": transcript_id},
    )


def run_forever() -> None:
    logger.info(
        "worker_started",
        extra={
            "poll_interval_ms": POLL_INTERVAL_MS,
            "mode": EXECUTION_MODE,
        },
    )

    while True:
        start = time.perf_counter()
        job = None

        try:
            job = claim_next_transcription_job()
            if not job:
                time.sleep(SLEEP_ON_EMPTY_MS / 1000.0)
                continue

            job_id = job["id"]
            video_id = job["video_id"]
            logger.info("job_running", extra={"job_id": job_id, "video_id": video_id})

            execute_transcription(job)
            mark_job_succeeded(job_id=job_id)

            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.info(
                "job_succeeded",
                extra={
                    "job_id": job_id,
                    "video_id": video_id,
                    "duration_ms": elapsed_ms,
                },
            )

        except Exception as e:
            if job:
                job_id = job.get("id")
                video_id = job.get("video_id")
                mark_job_failed(job_id=job_id, error_message=str(e))
                logger.exception(
                    "job_failed",
                    extra={"job_id": job_id, "video_id": video_id},
                )
            else:
                logger.exception("loop_failed")

            time.sleep(0.2)


def main() -> None:
    run_forever()


if __name__ == "__main__":
    main()
