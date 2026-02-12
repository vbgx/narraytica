from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

from ...config import settings
from ...telemetry.logging import get_logger

log = get_logger(__name__)

TEMPLATE_PATH = Path(__file__).parent / "templates" / "videos.template.json"


def _opensearch_url() -> str:
    # prefer settings (pydantic), fallback to env, then local default
    url = getattr(settings, "opensearch_url", None) or os.environ.get("OPENSEARCH_URL")
    return (url or "http://localhost:9200").rstrip("/")


def _timeout_seconds() -> float:
    # allow env override for tests
    v = os.environ.get("OPENSEARCH_TIMEOUT_SECONDS")
    if v:
        try:
            return float(v)
        except Exception:
            pass
    # fallback
    return 10.0


def _videos_index() -> str:
    return os.environ.get("OPENSEARCH_VIDEOS_INDEX", "narralytica-videos-v1")


def _videos_template_name() -> str:
    return os.environ.get(
        "OPENSEARCH_VIDEOS_TEMPLATE_NAME", "narralytica-videos-template"
    )


def _bootstrap_enabled() -> bool:
    v = os.environ.get("OPENSEARCH_BOOTSTRAP_ENABLED", "true").strip().lower()
    return v in ("1", "true", "yes", "y", "on")


def _request(method: str, url: str, **kwargs: Any) -> requests.Response:
    timeout = _timeout_seconds()
    return requests.request(method, url, timeout=timeout, **kwargs)


def ensure_opensearch_ready() -> bool:
    try:
        r = _request("GET", f"{_opensearch_url()}/_cluster/health")
        r.raise_for_status()
        return True
    except Exception as e:
        log.warning(
            "opensearch not ready",
            extra={"error": str(e), "url": _opensearch_url()},
        )
        return False


def put_videos_template() -> None:
    payload = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    template_name = _videos_template_name()
    url = f"{_opensearch_url()}/_index_template/{template_name}"

    r = _request("PUT", url, json=payload)
    r.raise_for_status()
    log.info("opensearch template installed", extra={"template": template_name})


def ensure_index(index_name: str) -> None:
    r = _request("HEAD", f"{_opensearch_url()}/{index_name}")
    if r.status_code == 200:
        log.info("opensearch index already exists", extra={"index": index_name})
        return
    if r.status_code not in (404,):
        r.raise_for_status()

    r2 = _request("PUT", f"{_opensearch_url()}/{index_name}")
    r2.raise_for_status()
    log.info("opensearch index created", extra={"index": index_name})


def bootstrap_opensearch() -> None:
    if not _bootstrap_enabled():
        log.info("opensearch bootstrap disabled")
        return

    if not ensure_opensearch_ready():
        return

    try:
        put_videos_template()
        ensure_index(_videos_index())
    except Exception as e:
        log.exception("opensearch bootstrap failed", extra={"error": str(e)})
