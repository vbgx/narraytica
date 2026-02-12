import logging
import os
import tempfile
import time
from typing import Any

from db.jobs import create_or_get_transcription_job
from db.videos import persist_video_metadata
from domain.job_status import JobStatus
from media.audio import extract_audio_wav_16k_mono
from metadata.ffprobe import probe_media
from metadata.normalize import normalize_video_metadata
from packages.shared.storage.s3_client import S3ObjectStorageClient
from telemetry.ingest import JobCtx, emit_metric, log_error, log_event, timed_phase
from upload.handler import migrate_upload_to_canonical
from youtube.downloader import download_youtube_video

logger = logging.getLogger("ingest-worker")


class IngestWorker:
    def __init__(self) -> None:
        log_event(
            JobCtx(job_id="bootstrap", video_id="bootstrap"),
            "ingest_worker_initialized",
        )

        self.storage = S3ObjectStorageClient(
            endpoint_url=os.getenv("S3_ENDPOINT"),
            access_key=os.getenv("S3_ACCESS_KEY"),
            secret_key=os.getenv("S3_SECRET_KEY"),
        )
        self.uploads_bucket = os.getenv("UPLOADS_BUCKET", "uploads")

    # ---------------------------------------------------------------------
    # Public entrypoint
    # ---------------------------------------------------------------------

    def run(self, job: dict[str, Any]) -> None:
        job_id = job["id"]
        video_id = job["video_id"]
        ctx = JobCtx(job_id=job_id, video_id=video_id)

        start = time.perf_counter()
        log_event(ctx, "job_started", job_type=job.get("type", "ingest"))

        try:
            self._update_status(job_id, JobStatus.RUNNING)

            # 1) Acquire canonical video
            with timed_phase(ctx, "downloading"):
                source_metadata, video_bucket, video_key = (
                    self._ensure_video_in_canonical_storage(job)
                )
                job["payload"].setdefault("extracted_metadata", {}).update(
                    source_metadata
                )

            # 2) Process (ffprobe + audio extraction)
            with timed_phase(
                ctx, "processing", video_bucket=video_bucket, video_key=video_key
            ):
                audio_bytes, ffprobe_video = self._extract_audio_and_probe(job)

            # 3) Store audio artifact
            with timed_phase(ctx, "storing"):
                audio_bucket, audio_key = self._store_audio_artifact(job, audio_bytes)

            # 4) Normalize + persist metadata
            with timed_phase(ctx, "metadata"):
                self._normalize_and_persist_metadata(
                    job=job,
                    ffprobe_video=ffprobe_video,
                    video_bucket=video_bucket,
                    video_key=video_key,
                    audio_bucket=audio_bucket,
                    audio_key=audio_key,
                )

            self._update_status(job_id, JobStatus.SUCCEEDED)
            self._clear_phase(job_id)

            total_ms = int((time.perf_counter() - start) * 1000)
            emit_metric(
                "ingest_job_duration_ms",
                total_ms,
                labels={"source": str(job["payload"]["source"].get("kind", "unknown"))},
            )
            log_event(ctx, "job_completed", duration_ms=total_ms)

        except Exception as e:
            total_ms = int((time.perf_counter() - start) * 1000)
            log_error(ctx, "job_failed", e, duration_ms=total_ms)

            # keep existing status updates
            self._fail_job(job_id, str(e))

    # ---------------------------------------------------------------------
    # Download / Acquire
    # ---------------------------------------------------------------------

    def _ensure_video_in_canonical_storage(
        self, job: dict[str, Any]
    ) -> tuple[dict[str, Any], str, str]:
        payload = job["payload"]
        source = payload["source"]
        artifacts = payload["artifacts"]

        video_bucket = artifacts["video"]["bucket"]
        video_key = artifacts["video"]["object_key"]

        kind = source.get("kind")
        if kind == "youtube":
            url = source.get("url")
            if not url:
                raise ValueError("youtube source requires url")

            video_bytes, metadata = download_youtube_video(url)
            self.storage.upload_bytes(video_bucket, video_key, video_bytes, "video/mp4")

            logger.info(
                "canonical_video_uploaded",
                extra={
                    "job_id": job["id"],
                    "video_id": job["video_id"],
                    "bucket": video_bucket,
                    "key": video_key,
                },
            )
            return metadata, video_bucket, video_key

        if kind == "upload":
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

            logger.info(
                "canonical_video_ready",
                extra={
                    "job_id": job["id"],
                    "video_id": job["video_id"],
                    "bucket": video_bucket,
                    "key": video_key,
                },
            )
            return (
                {"source_kind": "upload", "upload_migration": mig},
                video_bucket,
                video_key,
            )

        raise NotImplementedError(f"unsupported source.kind: {kind}")

    # ---------------------------------------------------------------------
    # Audio extraction + ffprobe
    # ---------------------------------------------------------------------

    def _extract_audio_and_probe(
        self, job: dict[str, Any]
    ) -> tuple[bytes, dict[str, Any]]:
        artifacts = job["payload"]["artifacts"]
        video_bucket = artifacts["video"]["bucket"]
        video_key = artifacts["video"]["object_key"]

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "source.mp4")
            audio_path = os.path.join(tmpdir, "audio.wav")

            logger.info(
                "download_video_for_processing",
                extra={
                    "job_id": job["id"],
                    "video_id": job["video_id"],
                    "bucket": video_bucket,
                    "key": video_key,
                },
            )
            self.storage.download_to_file(video_bucket, video_key, video_path)

            ffprobe_video = probe_media(video_path)
            extract_audio_wav_16k_mono(video_path, audio_path)

            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

        return audio_bytes, ffprobe_video

    # ---------------------------------------------------------------------
    # Store artifacts
    # ---------------------------------------------------------------------

    def _store_audio_artifact(
        self, job: dict[str, Any], audio_bytes: bytes
    ) -> tuple[str, str]:
        artifacts = job["payload"]["artifacts"]
        audio_bucket = artifacts["audio"]["bucket"]
        audio_key = artifacts["audio"]["object_key"]

        self.storage.upload_bytes(audio_bucket, audio_key, audio_bytes, "audio/wav")

        logger.info(
            "audio_uploaded",
            extra={
                "job_id": job["id"],
                "video_id": job["video_id"],
                "bucket": audio_bucket,
                "key": audio_key,
            },
        )
        return audio_bucket, audio_key

    # ---------------------------------------------------------------------
    # Normalize + Persist (02.09)
    # ---------------------------------------------------------------------

    def _normalize_and_persist_metadata(
        self,
        *,
        job: dict[str, Any],
        ffprobe_video: dict[str, Any],
        video_bucket: str,
        video_key: str,
        audio_bucket: str,
        audio_key: str,
    ) -> None:
        video_stat = self.storage.stat_object(video_bucket, video_key)
        audio_stat = self.storage.stat_object(audio_bucket, audio_key)

        source = job["payload"]["source"]
        source_kind = source.get("kind") or "unknown"
        # For uploads, source identifier is upload_ref; fallback to url when present
        source_uri = source.get("upload_ref") or source.get("url")

        norm = normalize_video_metadata(
            video_id=job["video_id"],
            source_platform=source_kind,
            ffprobe_video=ffprobe_video,
            video_stat=video_stat,
            audio_stat=audio_stat,
            extracted_metadata=job["payload"].get("extracted_metadata"),
        )

        persist_video_metadata(
            video_id=job["video_id"],
            source=source,
            artifacts=job["payload"].get("artifacts"),
            source_uri=source_uri,
            metadata={},  # keep minimal for integration tests
        )

        transcription_job_id, transcription_idempotency_key = (
            create_or_get_transcription_job(
                video_id=job["video_id"],
                audio_bucket=audio_bucket,
                audio_key=audio_key,
                audio_size_bytes=norm.audio_ref.size_bytes,
            )
        )

        log_event(
            JobCtx(job_id=job["id"], video_id=job["video_id"]),
            "transcription_job_queued",
            job_type="transcription",
            transcription_job_id=transcription_job_id,
            idempotency_key=transcription_idempotency_key,
            audio_bucket=audio_bucket,
            audio_key=audio_key,
        )

        logger.info(
            "video_metadata_persisted",
            extra={"job_id": job["id"], "video_id": job["video_id"]},
        )

    # ---------------------------------------------------------------------
    # State Management (to be wired to DB later)
    # ---------------------------------------------------------------------

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
