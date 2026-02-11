from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests
from config import settings
from telemetry.logging import get_logger

log = get_logger(__name__)

TEMPLATE_PATH = Path(__file__).parent / "templates" / "videos.template.json"


def _request(method: str, url: str, **kwargs: Any) -> requests.Response:
    timeout = settings.OPENSEARCH_TIMEOUT_SECONDS
    return requests.request(method, url, timeout=timeout, **kwargs)


def ensure_opensearch_ready() -> bool:
    try:
        r = _request("GET", f"{settings.OPENSEARCH_URL}/_cluster/health")
        r.raise_for_status()
        return True
    except Exception as e:
        log.warning(
            "opensearch not ready",
            extra={"error": str(e), "url": settings.OPENSEARCH_URL},
        )
        return False


def put_videos_template() -> None:
    payload = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    template_name = settings.OPENSEARCH_VIDEOS_TEMPLATE_NAME
    url = f"{settings.OPENSEARCH_URL}/_index_template/{template_name}"

    r = _request("PUT", url, json=payload)
    r.raise_for_status()
    log.info("opensearch template installed", extra={"template": template_name})


def ensure_index(index_name: str) -> None:
    # Create index only if missing (templates will apply)
    r = _request("HEAD", f"{settings.OPENSEARCH_URL}/{index_name}")
    if r.status_code == 200:
        log.info("opensearch index already exists", extra={"index": index_name})
        return
    if r.status_code not in (404,):
        r.raise_for_status()

    r2 = _request("PUT", f"{settings.OPENSEARCH_URL}/{index_name}")
    r2.raise_for_status()
    log.info("opensearch index created", extra={"index": index_name})


def bootstrap_opensearch() -> None:
    if not settings.OPENSEARCH_BOOTSTRAP_ENABLED:
        log.info("opensearch bootstrap disabled")
        return

    if not ensure_opensearch_ready():
        # do not crash API on startup; we just log
        return

    try:
        put_videos_template()
        ensure_index(settings.OPENSEARCH_VIDEOS_INDEX)
    except Exception as e:
        log.exception("opensearch bootstrap failed", extra={"error": str(e)})
