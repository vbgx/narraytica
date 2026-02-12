from __future__ import annotations

import os
from dataclasses import dataclass

import pytest

# -----------------------------------------------------------------------------
# Integration-test env defaults
# -----------------------------------------------------------------------------
os.environ.setdefault("OPENSEARCH_URL", "http://localhost:9200")
os.environ.setdefault("OPENSEARCH_SEGMENTS_INDEX", "narralytica-segments-v1")

os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_SEGMENTS_COLLECTION", "narralytica-segments-v1")

# Buckets (tests default to UPLOADS_BUCKET if missing)
os.environ.setdefault("UPLOADS_BUCKET", "uploads")
os.environ.setdefault("AUDIO_BUCKET", "audio-tracks")
os.environ.setdefault("TRANSCRIPTS_BUCKET", "transcripts")

# MinIO / S3 (ensure boto3 can connect)
os.environ.setdefault("S3_ENDPOINT", "http://localhost:9000")
os.environ.setdefault("S3_ACCESS_KEY", "minioadmin")
os.environ.setdefault("S3_SECRET_KEY", "minioadmin")
os.environ.setdefault("S3_REGION", "us-east-1")

# Also set AWS_* (boto3 standard)
os.environ.setdefault("AWS_ACCESS_KEY_ID", os.environ["S3_ACCESS_KEY"])
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", os.environ["S3_SECRET_KEY"])
os.environ.setdefault("AWS_DEFAULT_REGION", os.environ["S3_REGION"])


# -----------------------------------------------------------------------------
# Database URL (Postgres libpq DSN)
# -----------------------------------------------------------------------------
def _postgres_dsn() -> str:
    host = os.environ.get("POSTGRES_HOST", "127.0.0.1")
    port = os.environ.get("POSTGRES_PORT", "15432")
    db = os.environ.get("POSTGRES_DB", "narralytica")
    user = os.environ.get("POSTGRES_USER", "narralytica")
    pwd = os.environ.get("POSTGRES_PASSWORD", "narralytica")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


@pytest.fixture(scope="session")
def database_url() -> str:
    dsn = _postgres_dsn()
    os.environ["DATABASE_URL"] = dsn
    return dsn


# -----------------------------------------------------------------------------
# test_ids fixture (required by test_ingest_flow.py)
# -----------------------------------------------------------------------------
@pytest.fixture()
def test_ids() -> dict[str, str]:
    return {
        "video_id": "vid_test_01",
        "job_id": "job_test_01",
        "upload_id": "upl_test_01",
        "speaker_id": "spk_test_01",
        "transcript_id": "tr_test_01",
        "segment_id": "seg_test_01",
    }


# -----------------------------------------------------------------------------
# S3-compatible test storage (backed by MinIO via boto3)
# -----------------------------------------------------------------------------
@dataclass
class MinioTestStorage:
    endpoint: str
    access_key: str
    secret_key: str
    region: str

    def _client(self):
        import boto3

        return boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    def ensure_bucket(self, bucket: str) -> None:
        s3 = self._client()
        try:
            s3.head_bucket(Bucket=bucket)
            return
        except Exception:
            pass
        # MinIO accepts CreateBucket without LocationConstraint in many configs;
        # keeping it simple for local integration.
        s3.create_bucket(Bucket=bucket)

    # --- Methods used by tests -------------------------------------------------

    def upload_bytes(
        self, bucket: str, key: str, data: bytes, content_type: str | None = None
    ) -> None:
        s3 = self._client()
        kwargs = {"Bucket": bucket, "Key": key, "Body": data}
        if content_type:
            kwargs["ContentType"] = content_type
        s3.put_object(**kwargs)

    def download_bytes(self, bucket: str, key: str) -> bytes:
        s3 = self._client()
        r = s3.get_object(Bucket=bucket, Key=key)
        return r["Body"].read()

    def copy_object(
        self, src_bucket: str, src_key: str, dst_bucket: str, dst_key: str
    ) -> None:
        s3 = self._client()
        copy_source = {"Bucket": src_bucket, "Key": src_key}
        s3.copy_object(Bucket=dst_bucket, Key=dst_key, CopySource=copy_source)

    def delete_object(self, bucket: str, key: str) -> None:
        s3 = self._client()
        s3.delete_object(Bucket=bucket, Key=key)

    def stat_object(self, bucket: str, key: str) -> dict:
        s3 = self._client()
        h = s3.head_object(Bucket=bucket, Key=key)
        # Normalize to the contract expected by integration tests
        size = int(h.get("ContentLength") or 0)
        out = {"size_bytes": size}
        # Keep a few useful fields for debugging if needed
        if "ContentType" in h:
            out["content_type"] = h["ContentType"]
        if "ETag" in h:
            out["etag"] = h["ETag"]
        return out


@pytest.fixture(scope="session")
def storage() -> MinioTestStorage:
    st = MinioTestStorage(
        endpoint=os.environ["S3_ENDPOINT"],
        access_key=os.environ["S3_ACCESS_KEY"],
        secret_key=os.environ["S3_SECRET_KEY"],
        region=os.environ["S3_REGION"],
    )

    # Ensure buckets exist
    st.ensure_bucket(os.environ["UPLOADS_BUCKET"])
    st.ensure_bucket(os.environ["AUDIO_BUCKET"])
    st.ensure_bucket(os.environ["TRANSCRIPTS_BUCKET"])

    return st
