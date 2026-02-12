from __future__ import annotations

import os
import time
from typing import Any

import requests


def _os_url() -> str:
    return (os.environ.get("OPENSEARCH_URL") or "http://localhost:9200").rstrip("/")


def _os_index() -> str:
    return os.environ.get("OPENSEARCH_SEGMENTS_INDEX") or "narralytica-segments-v1"


def wait_opensearch_ready(timeout_s: float = 10.0) -> None:
    url = _os_url()
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}/_cluster/health", timeout=2)
            if r.status_code == 200:
                return
        except Exception as e:
            last_err = e
        time.sleep(0.25)
    raise RuntimeError(f"OpenSearch not ready at {url}. last_err={last_err}")


def recreate_index_with_min_mapping() -> None:
    """
    Minimal mapping sufficient for /search route:
    requires _source contains video_id/start_ms/end_ms/text (+ optional filters fields).
    """
    url = _os_url()
    idx = _os_index()

    # delete if exists
    requests.delete(f"{url}/{idx}", timeout=5)

    mapping: dict[str, Any] = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "refresh_interval": "1s",
        },
        "mappings": {
            "properties": {
                "video_id": {"type": "keyword"},
                "transcript_id": {"type": "keyword"},
                "speaker_id": {"type": "keyword"},
                "segment_index": {"type": "integer"},
                "start_ms": {"type": "integer"},
                "end_ms": {"type": "integer"},
                "text": {"type": "text"},
                "language": {"type": "keyword"},
                "source": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
    }

    r = requests.put(f"{url}/{idx}", json=mapping, timeout=10)
    r.raise_for_status()


def bulk_seed_segments() -> None:
    url = _os_url()
    idx = _os_index()

    now = "2024-01-01T00:00:00Z"
    docs = [
        (
            "seg_01",
            {
                "video_id": "vid_01",
                "start_ms": 0,
                "end_ms": 1000,
                "text": "hello world",
                "language": "en",
                "source": "youtube",
                "created_at": now,
                "updated_at": now,
            },
        ),
        (
            "seg_02",
            {
                "video_id": "vid_01",
                "start_ms": 1000,
                "end_ms": 2000,
                "text": "hello again",
                "language": "en",
                "source": "youtube",
                "created_at": now,
                "updated_at": now,
            },
        ),
        (
            "seg_03",
            {
                "video_id": "vid_02",
                "start_ms": 0,
                "end_ms": 1000,
                "text": "bonjour monde",
                "language": "fr",
                "source": "youtube",
                "created_at": now,
                "updated_at": now,
            },
        ),
    ]

    lines = []
    for _id, src in docs:
        lines.append({"index": {"_index": idx, "_id": _id}})
        lines.append(src)

    ndjson = "\n".join([requests.utils.json.dumps(x) for x in lines]) + "\n"
    r = requests.post(
        f"{url}/_bulk",
        data=ndjson,
        headers={"Content-Type": "application/x-ndjson"},
        timeout=10,
    )
    r.raise_for_status()

    # refresh for immediate searchability
    requests.post(f"{url}/{idx}/_refresh", timeout=5).raise_for_status()
