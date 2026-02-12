from __future__ import annotations

import json
import os
import sys

from packages.shared.storage.s3_client import S3ObjectStorageClient

from .artifacts import iter_embedding_items, load_json_artifact
from .build_docs import build_segment_doc
from .db import update_job_status
from .opensearch.client import OpenSearchClient
from .qdrant.client import QdrantClient


def _env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    if v is None:
        return default
    v = v.strip()
    return v or default


def _load_job_payload() -> dict:
    raw = _env("JOB_PAYLOAD")
    if raw:
        return json.loads(raw)

    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data and data.strip():
            return json.loads(data)

    if len(sys.argv) >= 2:
        return json.loads(sys.argv[1])

    raise RuntimeError(
        "missing job payload: provide JOB_PAYLOAD, stdin json, or argv json"
    )


def _index_name() -> str:
    default = "narralytica-segments-v1"
    return _env("OPENSEARCH_SEGMENTS_INDEX", default) or default


def _qdrant_collection() -> str:
    default = "narralytica-segments-v1"
    return _env("QDRANT_SEGMENTS_COLLECTION", default) or default


def main() -> int:
    job = _load_job_payload()

    job_id = str(job.get("job_id") or "")
    video_id = str(job.get("video_id") or "")
    segments_ref = job.get("segments_ref")
    layers_ref = job.get("layers_ref")
    embeddings_ref = job.get("embeddings_ref")
    reindex = bool(job.get("reindex") or False)

    if not job_id or not video_id:
        raise RuntimeError("job payload must include job_id and video_id")

    update_job_status(job_id, "running")

    storage = S3ObjectStorageClient(
        endpoint_url=_env("S3_ENDPOINT_URL"),
        access_key=_env("S3_ACCESS_KEY"),
        secret_key=_env("S3_SECRET_KEY"),
        region=_env("S3_REGION", "us-east-1") or "us-east-1",
    )
    default_bucket = _env("S3_DEFAULT_BUCKET")

    segments_payload = load_json_artifact(
        storage, segments_ref, default_bucket=default_bucket
    )
    layers_payload = (
        load_json_artifact(storage, layers_ref, default_bucket=default_bucket)
        if layers_ref
        else None
    )
    embeddings_payload = (
        load_json_artifact(storage, embeddings_ref, default_bucket=default_bucket)
        if embeddings_ref
        else None
    )

    transcript_meta = None
    tenant_id = None
    transcript_id = None

    if isinstance(segments_payload, dict):
        transcript_meta = (
            segments_payload.get("transcript")
            if isinstance(segments_payload.get("transcript"), dict)
            else None
        )
        tenant_id = segments_payload.get("tenant_id")
        transcript_id = segments_payload.get("transcript_id") or (
            transcript_meta.get("id") if transcript_meta else None
        )

    if isinstance(segments_payload, dict) and isinstance(
        segments_payload.get("segments"), list
    ):
        segments = segments_payload["segments"]
    elif isinstance(segments_payload, list):
        segments = segments_payload
    else:
        raise RuntimeError(
            "segments artifact must be a list or an object with a 'segments' list"
        )

    layers_by_segment_id: dict[str, dict] = {}
    if isinstance(layers_payload, dict):
        items = layers_payload.get("items")
        if isinstance(items, list):
            for it in items:
                if (
                    isinstance(it, dict)
                    and it.get("segment_id")
                    and isinstance(it.get("data"), dict)
                ):
                    layers_by_segment_id[str(it["segment_id"])] = it["data"]

        by_id = layers_payload.get("by_segment_id")
        if isinstance(by_id, dict):
            for sid, data in by_id.items():
                if isinstance(data, dict):
                    layers_by_segment_id[str(sid)] = data

    docs: list[dict] = []
    payload_by_segment_id: dict[str, dict] = {}

    for seg in segments:
        if not isinstance(seg, dict):
            continue
        sdoc = build_segment_doc(
            video_id=video_id,
            transcript_id=str(transcript_id) if transcript_id else None,
            tenant_id=str(tenant_id) if tenant_id else None,
            segment=seg,
            transcript_meta=transcript_meta,
            layers_by_segment_id=layers_by_segment_id if layers_by_segment_id else None,
        )
        docs.append(sdoc.doc)
        payload_by_segment_id[sdoc.segment_id] = sdoc.qdrant_payload

    os_client = OpenSearchClient(
        base_url=_env("OPENSEARCH_URL") or "http://localhost:9200",
        username=_env("OPENSEARCH_USERNAME"),
        password=_env("OPENSEARCH_PASSWORD"),
        timeout_s=float(_env("OPENSEARCH_TIMEOUT_S", "10") or "10"),
    )

    q_client = QdrantClient(
        base_url=_env("QDRANT_URL") or "http://localhost:6333",
        api_key=_env("QDRANT_API_KEY"),
        timeout_s=float(_env("QDRANT_TIMEOUT_S", "15") or "15"),
    )

    index = _index_name()
    collection = _qdrant_collection()
    batch_size = int(_env("INDEXER_BATCH_SIZE", "500") or "500")

    for i in range(0, len(docs), batch_size):
        os_client.bulk_upsert(index=index, docs=docs[i : i + batch_size])

    if reindex:
        os_client.refresh(index=index)

    if embeddings_payload is None:
        raise RuntimeError(
            "embeddings_ref missing or embeddings artifact is null; check enrich worker"
        )

    expected_dim = int(_env("EMBEDDING_VECTOR_SIZE", "1024") or "1024")

    points: list[dict] = []
    for it in iter_embedding_items(embeddings_payload):
        sid = it.get("segment_id") or it.get("id")
        vec = it.get("vector") or it.get("embedding") or it.get("values")
        if not sid or vec is None:
            continue
        sid = str(sid)
        if not isinstance(vec, list):
            continue
        if len(vec) != expected_dim:
            raise RuntimeError(
                f"embedding dim mismatch for segment_id={sid}: "
                f"got={len(vec)} expected={expected_dim}"
            )
        payload = payload_by_segment_id.get(sid) or {
            "segment_id": sid,
            "video_id": video_id,
        }
        points.append({"id": sid, "vector": vec, "payload": payload})

        if len(points) >= batch_size:
            q_client.upsert_points(collection=collection, points=points)
            points = []

    if points:
        q_client.upsert_points(collection=collection, points=points)

    update_job_status(job_id, "completed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        job_id = None
        try:
            job = _load_job_payload()
            if isinstance(job, dict) and job.get("job_id"):
                job_id = str(job["job_id"])
        except Exception:
            job_id = None

        if job_id:
            try:
                update_job_status(job_id, "failed", error=str(e))
            except Exception:
                pass

        print(f"indexer failed: {e}", file=sys.stderr)
        raise
