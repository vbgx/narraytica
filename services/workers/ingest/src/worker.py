import logging
from typing import Any

from domain.job_status import JobStatus

logger = logging.getLogger("ingest-worker")


class IngestWorker:
    def __init__(self):
        logger.info("ingest_worker_initialized")

    # -------------------------
    # Public entrypoint
    # -------------------------
    def run(self, job: dict[str, Any]) -> None:
        job_id = job["id"]
        logger.info("job_started", extra={"job_id": job_id})

        try:
            self._update_status(job_id, JobStatus.RUNNING)

            self._update_phase(job_id, "downloading")
            self._download_media(job)

            self._update_phase(job_id, "processing")
            self._extract_audio(job)

            self._update_phase(job_id, "storing")
            self._store_artifacts(job)

            self._update_status(job_id, JobStatus.SUCCEEDED)
            self._clear_phase(job_id)

            logger.info("job_completed", extra={"job_id": job_id})

        except Exception as e:
            logger.exception("job_failed", extra={"job_id": job_id})
            self._fail_job(job_id, str(e))

    # -------------------------
    # Phase Methods (Mocked)
    # -------------------------

    def _download_media(self, job: dict[str, Any]) -> None:
        logger.info("mock_download_media", extra={"job_id": job["id"]})

    def _extract_audio(self, job: dict[str, Any]) -> None:
        logger.info("mock_extract_audio", extra={"job_id": job["id"]})

    def _store_artifacts(self, job: dict[str, Any]) -> None:
        logger.info("mock_store_artifacts", extra={"job_id": job["id"]})

    # -------------------------
    # State Management (to be wired to DB later)
    # -------------------------

    def _update_status(self, job_id: str, status: JobStatus) -> None:
        logger.info("job_status_update", extra={"job_id": job_id, "status": status})

    def _update_phase(self, job_id: str, phase: str) -> None:
        logger.info("job_phase_update", extra={"job_id": job_id, "phase": phase})

    def _clear_phase(self, job_id: str) -> None:
        logger.info("job_phase_cleared", extra={"job_id": job_id})

    def _fail_job(self, job_id: str, error_message: str) -> None:
        logger.error(
            "job_marked_failed",
            extra={"job_id": job_id, "error": error_message},
        )
