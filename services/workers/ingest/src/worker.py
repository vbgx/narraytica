import logging
import os
from typing import Any

from domain.job_status import JobStatus
from packages.shared.storage.s3_client import S3ObjectStorageClient
from upload.handler import migrate_upload_to_canonical
from youtube.downloader import download_youtube_video

logger = logging.getLogger("ingest-worker")


class IngestWorker:
    def __init__(self) -> None:
        logger.info("ingest_worker_initialized")

        self.storage = S3ObjectStorageClient(
            endpoint_url=os.getenv("S3_ENDPOINT"),
            access_key=os.getenv("S3_ACCESS_KEY"),
            secret_key=os.getenv("S3_SECRET_KEY"),
        )

        # Staging bucket for direct uploads (API upload flow)
        self.uploads_bucket = os.getenv("UPLOADS_BUCKET", "uploads")

    # -------------------------
    # Public entrypoint
    # -------------------------
    def run(self, job: dict[str, Any]) -> None:
        job_id = job["id"]
        logger.info("job_started", extra={"job_id": job_id})

        try:
            self._update_status(job_id, JobStatus.RUNNING)

            self._update_phase(job_id, "downloading")
            video_bytes, source_metadata = self._download_media(job)

            self._update_phase(job_id, "processing")
            audio_bytes = self._extract_audio(job, video_bytes)

            self._update_phase(job_id, "storing")
            self._store_artifacts(job, video_bytes, audio_bytes)

            job["payload"].setdefault("extracted_metadata", {}).update(source_metadata)

            self._update_status(job_id, JobStatus.SUCCEEDED)
            self._clear_phase(job_id)

            logger.info("job_completed", extra={"job_id": job_id})

        except Exception as e:
            logger.exception("job_failed", extra={"job_id": job_id})
            self._fail_job(job_id, str(e))

    # -------------------------
    # Phase Methods
    # -------------------------

    def _download_media(self, job: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
        logger.info("download_media_start", extra={"job_id": job["id"]})

        payload = job["payload"]
        source = payload["source"]
        artifacts = payload["artifacts"]

        # ---- YouTube
        if source["kind"] == "youtube":
            video_bytes, metadata = download_youtube_video(source["url"])
            logger.info("youtube_download_success", extra={"job_id": job["id"]})
            return video_bytes, metadata

        # ---- Upload (already in object storage staging)
        if source["kind"] == "upload":
            # Support both "upload_ref" and "object_key" naming (transition-friendly)
            upload_key = source.get("upload_ref") or source.get("object_key")
            if not upload_key:
                raise ValueError("upload source requires upload_ref or object_key")

            canonical_bucket = artifacts["video"]["bucket"]
            canonical_key = artifacts["video"]["object_key"]

            mig = migrate_upload_to_canonical(
                self.storage,
                upload_bucket=self.uploads_bucket,
                upload_key=upload_key,
                canonical_bucket=canonical_bucket,
                canonical_key=canonical_key,
            )

            # No need to load bytes into memory for upload path
            # The video is now available at canonical location.
            metadata = {
                "source_kind": "upload",
                "upload_migration": mig,
            }
            return b"", metadata

        raise NotImplementedError(f"unsupported source.kind: {source['kind']}")

    def _extract_audio(self, job: dict[str, Any], video_bytes: bytes) -> bytes:
        logger.info("mock_extract_audio", extra={"job_id": job["id"]})
        # ffmpeg integration comes in a later issue
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

        # For YouTube path, we have video bytes to upload.
        # For upload path, video is already in canonical storage,
        # migrated earlier in _download_media.
        if video_bytes:
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
