from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OpenSearchConfig:
    url: str
    segments_index: str
    timeout_s: float = 10.0
    username: str | None = None
    password: str | None = None

    @property
    def auth(self) -> tuple[str, str] | None:
        if self.username and self.password:
            return (self.username, self.password)
        return None


@dataclass(frozen=True)
class QdrantConfig:
    url: str
    segments_collection: str
    timeout_s: float = 10.0


@dataclass(frozen=True)
class SearchInfraConfig:
    opensearch: OpenSearchConfig
    qdrant: QdrantConfig


def from_env() -> SearchInfraConfig:
    os_url = (os.environ.get("OPENSEARCH_URL") or "").strip().rstrip("/")
    if not os_url:
        raise RuntimeError("OPENSEARCH_URL not configured")

    os_index = (os.environ.get("OPENSEARCH_SEGMENTS_INDEX") or "").strip()
    if not os_index:
        raise RuntimeError("OPENSEARCH_SEGMENTS_INDEX not configured")

    os_timeout = float((os.environ.get("OPENSEARCH_TIMEOUT_S") or "10").strip() or "10")

    q_url = (
        (os.environ.get("QDRANT_URL") or "http://localhost:6333").strip().rstrip("/")
    )
    q_coll = (
        os.environ.get("QDRANT_SEGMENTS_COLLECTION") or "narralytica-segments-v1"
    ).strip()
    q_timeout = float((os.environ.get("QDRANT_TIMEOUT_S") or "10").strip() or "10")

    return SearchInfraConfig(
        opensearch=OpenSearchConfig(
            url=os_url,
            segments_index=os_index,
            timeout_s=os_timeout,
            username=os.environ.get("OPENSEARCH_USERNAME"),
            password=os.environ.get("OPENSEARCH_PASSWORD"),
        ),
        qdrant=QdrantConfig(
            url=q_url,
            segments_collection=q_coll,
            timeout_s=q_timeout,
        ),
    )
