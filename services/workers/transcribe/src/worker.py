from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any
from uuid import uuid4

from asr.errors import AsrError
from asr.registry import get_provider
from audio_fetch import fetch_audio_to_tmp, resolve_audio_ref
from lang import detect_language, extract_language_hint, normalize_language
from packages.shared.storage.s3_client import S3ObjectStorageClient
from segmenter.timecodes import normalize_segments

from db.jobs import (
    claim_next_transcription_job,
    mark_job_failed,
    mark_job_succeeded,
)
from db.transcripts import insert_transcript

logger = logging.getLogger("transcribe-worker")

TRANSCRIPT_ARTIFACT_VERSION = "v1"


def _transcript_artifact_key(
    *, video_id: str, job_id: str, version: str = TRANSCRIPT_ARTIFACT_VERSION
) -> str:
    return f"transcripts/{video_id}/{job_id}/transcript.{version}.json"


def _s3_client() -> S3ObjectStorageClient:
    endpoint = os.getenv("S3_ENDPOINT")
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")

    if not (endpoint and access_key and secret_key):
        raise RuntimeError(
            "S3 creds missing: S3_ENDPOINT/S3_ACCESS_KEY/S3_SECRET_KEY must be set"
        )

    return S3ObjectStorageClient(
        endpoint_url=endpoint,
        access_key=access_key,
        secret_key=secret_key,
    )


def _upload_transcript_artifact(
    *,
    video_id: str,
    job_id: str,
    transcript_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Store transcript payload as JSON artifact in object storage.

    Returns:
      {bucket, key, size_bytes, sha256}
    """
    storage = _s3_client()

    bucket = os.getenv("TRANSCRIPTS_BUCKET", "transcripts")
    key = _transcript_artifact_key(video_id=video_id, job_id=job_id)

    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    sha256 = hashlib.sha256(raw).hexdigest()

    storage.upload_bytes(bucket, key, raw, "application/json")

    return {
        "bucket": bucket,
        "key": key,
        "size_bytes": len(raw),
        "sha256": sha256,
    }


def _build_storage_ref(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": "minio",
        "bucket": artifact["bucket"],
        "key": artifact["key"],
        "content_type": "application/json",
        "size_bytes": artifact["size_bytes"],
        "checksum": f"sha256:{artifact['sha256']}",
    }


def _run_asr(job: dict[str, Any]) -> None:
    """
    v0:
      - fetch audio from object storage (MinIO/S3)
      - run ASR via pluggable provider
      - store transcript artifact (json) in object storage
      - persist transcript row + artifact pointers
    """
    job_id = str(job["id"])
    video_id = str(job["video_id"])
    payload = job.get("payload") or {}

    bucket, key = resolve_audio_ref(payload)
    audio_path = fetch_audio_to_tmp(bucket=bucket, key=key)

    provider = get_provider()
    res = provider.transcribe(audio_path=audio_path)

    # Language resolution (deterministic): provider > hint > detection
    language_hint = extract_language_hint(payload)
    provider_lang = normalize_language(res.language)
    if provider_lang:
        language_final = provider_lang
        language_source = "provider"
    elif language_hint:
        language_final = language_hint
        language_source = "hint"
    else:
        language_final = detect_language(res.text)
        language_source = "detected"

    logger.info(
        "language_resolved",
        extra={
            "job_id": job_id,
            "video_id": video_id,
            "provider": provider.name,
            "language": language_final,
            "language_source": language_source,
            "language_hint": language_hint,
            "provider_language": res.language,
        },
    )

    transcript_id = str(uuid4())

    transcript_payload: dict[str, Any] = {
        "transcript_id": transcript_id,
        "job_id": job_id,
        "artifact_version": TRANSCRIPT_ARTIFACT_VERSION,
        "video_id": video_id,
        "provider": provider.name,
        "language": language_final,
        "text": res.text,
        "segments": normalize_segments(
            [
                {"start_s": s.start_s, "end_s": s.end_s, "text": s.text}
                for s in res.segments
            ]
        ),
        "asr": res.raw,
        "audio_ref": {"bucket": bucket, "key": key},
    }

    # Derive duration from canonical segments (ms -> seconds)
    _segs = transcript_payload.get("segments") or []
    _duration_ms = int(_segs[-1].get("end_ms", 0)) if _segs else 0
    duration_seconds = _duration_ms / 1000.0

    artifact = _upload_transcript_artifact(
        video_id=video_id,
        job_id=job_id,
        transcript_id=transcript_id,
        payload=transcript_payload,
    )
    storage_ref = _build_storage_ref(artifact)

    transcript_payload["storage_ref"] = storage_ref
    # note: artifact JSON includes storage_ref so it is self-describing
    # and retrievable by ref

    insert_transcript(
        transcript_id=transcript_id,
        video_id=video_id,
        provider=provider.name,
        language=language_final,
        duration_seconds=duration_seconds,
        status="completed",
        metadata=transcript_payload,
        artifact_bucket=artifact["bucket"],
        artifact_key=artifact["key"],
        artifact_format="json",
        artifact_bytes=artifact["size_bytes"],
        artifact_sha256=artifact["sha256"],
        storage_ref=storage_ref,
    )

    logger.info(
        "transcription_completed",
        extra={
            "job_id": job_id,
            "video_id": video_id,
            "provider": provider.name,
            "language": language_final,
            "text_chars": len(res.text or ""),
            "artifact_bucket": artifact["bucket"],
            "artifact_key": artifact["key"],
        },
    )


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
    logger.info("worker_started")

    while True:
        job = claim_next_transcription_job()
        if not job:
            return

        job_id = str(job["id"])
        logger.info(
            "job_claimed",
            extra={
                "job_id": job_id,
                "job_type": job.get("type"),
            },
        )

        try:
            _run_asr(job)
            mark_job_succeeded(job_id=job_id)
            logger.info("job_succeeded", extra={"job_id": job_id})
        except AsrError as e:
            mark_job_failed(
                job_id=job_id,
                error_message=f"{e.code}: {str(e)}",
            )
            logger.exception(
                "job_failed_asr",
                extra={
                    "job_id": job_id,
                    "code": e.code,
                },
            )
        except Exception as e:
            mark_job_failed(
                job_id=job_id,
                error_message=f"transcribe_unexpected_error: {str(e)}",
            )
            logger.exception("job_failed", extra={"job_id": job_id})


if __name__ == "__main__":
    main()
