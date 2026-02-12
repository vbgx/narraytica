from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from asr.errors import ASR_ERR_AUDIO_DOWNLOAD_FAILED, AsrError
from packages.shared.storage.s3_client import S3ObjectStorageClient


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


def fetch_audio_to_tmp(*, bucket: str, key: str, filename: str = "audio.wav") -> str:
    """
    Download audio artifact from object storage into a temporary directory.
    Returns the local file path.
    """
    storage = _s3_client()

    tmpdir = Path(tempfile.mkdtemp(prefix="narralytica-audio-"))
    out_path = tmpdir / filename

    try:
        storage.download_to_file(bucket, key, str(out_path))
        return str(out_path)
    except Exception as e:
        raise AsrError(ASR_ERR_AUDIO_DOWNLOAD_FAILED, str(e)) from e


def resolve_audio_ref(job_payload: dict[str, Any]) -> tuple[str, str]:
    """
    Accepts (in order):
      1) payload.audio_storage_ref = {bucket, key}
      2) payload.artifacts.audio = {bucket, object_key|key}
    """
    ref = job_payload.get("audio_storage_ref")
    if isinstance(ref, dict):
        b = ref.get("bucket")
        k = ref.get("key")
        if b and k:
            return str(b), str(k)

    artifacts = job_payload.get("artifacts")
    if isinstance(artifacts, dict):
        audio = artifacts.get("audio")
        if isinstance(audio, dict):
            b = audio.get("bucket")
            k = audio.get("object_key") or audio.get("key")
            if b and k:
                return str(b), str(k)

    raise AsrError("asr_audio_ref_missing", "missing audio ref in job.payload")
