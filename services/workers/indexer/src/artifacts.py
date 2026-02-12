import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from packages.shared.storage.s3_client import S3ObjectStorageClient


@dataclass(frozen=True)
class StorageRef:
    bucket: str
    key: str


def _parse_storage_ref(value: Any, default_bucket: str | None = None) -> StorageRef:
    if value is None:
        raise ValueError("storage ref is null")

    if isinstance(value, dict):
        bucket = value.get("bucket") or value.get("Bucket") or value.get("b")
        key = value.get("key") or value.get("Key") or value.get("k")
        if not bucket or not key:
            raise ValueError(f"invalid storage ref dict: {value}")
        return StorageRef(bucket=str(bucket), key=str(key))

    if isinstance(value, str):
        s = value.strip()
        if not s:
            raise ValueError("storage ref is empty string")

        if s.startswith("s3://") or s.startswith("minio://"):
            s2 = s.split("://", 1)[1]
            parts = s2.split("/", 1)
            if len(parts) != 2:
                raise ValueError(f"invalid storage uri: {value}")
            return StorageRef(bucket=parts[0], key=parts[1])

        if s.startswith("{") and s.endswith("}"):
            try:
                obj = json.loads(s)
                return _parse_storage_ref(obj, default_bucket=default_bucket)
            except Exception as e:
                raise ValueError(f"invalid storage ref json string: {e}") from e

        if ":" in s and s.count(":") == 1 and "/" not in s.split(":", 1)[0]:
            bucket, key = s.split(":", 1)
            if bucket and key:
                return StorageRef(bucket=bucket, key=key)

        if "/" in s:
            if default_bucket:
                return StorageRef(bucket=default_bucket, key=s)
            parts = s.split("/", 1)
            return StorageRef(bucket=parts[0], key=parts[1])

        if default_bucket:
            return StorageRef(bucket=default_bucket, key=s)

    raise ValueError(f"unsupported storage ref type: {type(value)}")


def load_json_artifact(
    storage: S3ObjectStorageClient,
    ref_value: Any,
    default_bucket: str | None = None,
) -> Any:
    ref = _parse_storage_ref(ref_value, default_bucket=default_bucket)
    raw = storage.download_bytes(ref.bucket, ref.key)
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise ValueError(
            f"artifact is not valid json: bucket={ref.bucket} key={ref.key} err={e}"
        ) from e


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def iter_embedding_items(embeddings_payload: Any) -> Iterable[dict]:
    if embeddings_payload is None:
        return []
    if isinstance(embeddings_payload, dict):
        if "items" in embeddings_payload and isinstance(
            embeddings_payload["items"], list
        ):
            for it in embeddings_payload["items"]:
                if isinstance(it, dict):
                    yield it
            return
        if "embeddings" in embeddings_payload and isinstance(
            embeddings_payload["embeddings"], list
        ):
            for it in embeddings_payload["embeddings"]:
                if isinstance(it, dict):
                    yield it
            return
        if "by_segment_id" in embeddings_payload and isinstance(
            embeddings_payload["by_segment_id"], dict
        ):
            for sid, vec in embeddings_payload["by_segment_id"].items():
                yield {"segment_id": sid, "vector": vec}
            return
    if isinstance(embeddings_payload, list):
        for it in embeddings_payload:
            if isinstance(it, dict):
                yield it
        return
    return []
