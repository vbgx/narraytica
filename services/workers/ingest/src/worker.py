import logging
import os
from typing import Any

from domain.job_status import JobStatus
from packages.shared.storage.s3_client import S3ObjectStorageClient

logger = logging.getLogger("ingest-worker")


class IngestWorker:
    def __init__(self) -> None:
        logger.info("ingest_worker_initialized")

        self.storage = S3ObjectStorageClient(
            endpoint_url=os.getenv("S3_ENDPOINT"),
            access_key=os.getenv("S3_ACCESS_KEY"),
            secret_key=os.getenv("S3_SECRET_KEY"),
        )

    # -------------------------
    # Public entrypoint
    # -------------------------
    def run(self, job: dict[str, Any]) -> None:
        job_id = job["id"]
        logger.info("job_started", extra={"job_id": job_id})

        try:
            self._update_status(job_id, JobStatus.RUNNING)

            self._update_phase(job_id, "downloading")
            video_bytes = self._download_media(job)

            self._update_phase(job_id, "processing")
            audio_bytes = self._extract_audio(job, video_bytes)

            self._update_phase(job_id, "storing")
            self._store_artifacts(job, video_bytes, audio_bytes)

            self._update_status(job_id, JobStatus.SUCCEEDED)
            self._clear_phase(job_id)

            logger.info("job_completed", extra={"job_id": job_id})

        except Exception as e:
            logger.exception("job_failed", extra={"job_id": job_id})
            self._fail_job(job_id, str(e))

    # -------------------------
    # Phase Methods (Mocked I/O)
    # -------------------------

    def _download_media(self, job: dict[str, Any]) -> bytes:
        logger.info("mock_download_media", extra={"job_id": job["id"]})
        return b"fake video data"

    def _extract_audio(self, job: dict[str, Any], video_bytes: bytes) -> bytes:
        logger.info("mock_extract_audio", extra={"job_id": job["id"]})
        return b"fake audio data"

    def _store_artifacts(
        self,
        job: dict[str, Any],
        video_bytes: bytes,
        audio_bytes: bytes,
    ) -> None:
        logger.info("uploading_artifacts", extra={"job_id": job["id"]})

        artifacts = job["payload"]["artifacts"]

        video_bucket = artifacts["video"]["bucket"]
        video_key = artifacts["video"]["object_key"]

        audio_bucket = artifacts["audio"]["bucket"]
        audio_key = artifacts["audio"]["object_key"]

        self.storage.upload_bytes(video_bucket, video_key, video_bytes, "video/mp4")
        self.storage.upload_bytes(audio_bucket, audio_key, audio_bytes, "audio/wav")

        logger.info("artifacts_uploaded", extra={"job_id": job["id"]})

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
