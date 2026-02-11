import logging
import os
import tempfile
from typing import Any

from domain.job_status import JobStatus
from media.audio import extract_audio_wav_16k_mono
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
        self.uploads_bucket = os.getenv("UPLOADS_BUCKET", "uploads")

    def run(self, job: dict[str, Any]) -> None:
        job_id = job["id"]
        logger.info("job_started", extra={"job_id": job_id})

        try:
            self._update_status(job_id, JobStatus.RUNNING)

            self._update_phase(job_id, "downloading")
            source_metadata = self._ensure_video_in_canonical_storage(job)

            self._update_phase(job_id, "processing")
            audio_bytes = self._extract_audio_from_canonical_video(job)

            self._update_phase(job_id, "storing")
            self._store_audio_artifact(job, audio_bytes)

            job["payload"].setdefault("extracted_metadata", {}).update(source_metadata)

            self._update_status(job_id, JobStatus.SUCCEEDED)
            self._clear_phase(job_id)

            logger.info("job_completed", extra={"job_id": job_id})

        except Exception as e:
            logger.exception("job_failed", extra={"job_id": job_id})
            self._fail_job(job_id, str(e))

    # -------------------------
    # Download / Acquire
    # -------------------------

    def _ensure_video_in_canonical_storage(self, job: dict[str, Any]) -> dict[str, Any]:
        payload = job["payload"]
        source = payload["source"]
        artifacts = payload["artifacts"]

        video_bucket = artifacts["video"]["bucket"]
        video_key = artifacts["video"]["object_key"]

        if source["kind"] == "youtube":
            video_bytes, metadata = download_youtube_video(source["url"])
            self.storage.upload_bytes(video_bucket, video_key, video_bytes, "video/mp4")
            logger.info("canonical_video_uploaded", extra={"job_id": job["id"]})
            return metadata

        if source["kind"] == "upload":
            upload_key = source.get("upload_ref") or source.get("object_key")
            if not upload_key:
                raise ValueError("upload source requires upload_ref or object_key")

            mig = migrate_upload_to_canonical(
                self.storage,
                upload_bucket=self.uploads_bucket,
                upload_key=upload_key,
                canonical_bucket=video_bucket,
                canonical_key=video_key,
            )
            logger.info("canonical_video_ready", extra={"job_id": job["id"]})
            return {"source_kind": "upload", "upload_migration": mig}

        raise NotImplementedError(f"unsupported source.kind: {source['kind']}")

    # -------------------------
    # Audio extraction (ffmpeg)
    # -------------------------

    def _extract_audio_from_canonical_video(self, job: dict[str, Any]) -> bytes:
        artifacts = job["payload"]["artifacts"]

        video_bucket = artifacts["video"]["bucket"]
        video_key = artifacts["video"]["object_key"]

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "source.mp4")
            audio_path = os.path.join(tmpdir, "audio.wav")

            logger.info(
                "download_video_for_ffmpeg",
                extra={"job_id": job["id"], "bucket": video_bucket, "key": video_key},
            )
            self.storage.download_to_file(video_bucket, video_key, video_path)

            extract_audio_wav_16k_mono(video_path, audio_path)

            with open(audio_path, "rb") as f:
                return f.read()

    # -------------------------
    # Store artifacts
    # -------------------------

    def _store_audio_artifact(self, job: dict[str, Any], audio_bytes: bytes) -> None:
        artifacts = job["payload"]["artifacts"]
        audio_bucket = artifacts["audio"]["bucket"]
        audio_key = artifacts["audio"]["object_key"]

        self.storage.upload_bytes(audio_bucket, audio_key, audio_bytes, "audio/wav")
        logger.info(
            "audio_uploaded",
            extra={"job_id": job["id"], "bucket": audio_bucket, "key": audio_key},
        )

        # TODO (DB wiring):
        # persist storage reference in DB (bucket + key) for the audio artifact

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
            "job_marked_failed", extra={"job_id": job_id, "error": error_message}
        )
