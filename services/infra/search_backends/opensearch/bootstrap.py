from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import httpx


def _env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    if v is None:
        return default
    v = v.strip()
    return v or default


@dataclass(frozen=True)
class OpenSearchBootstrap:
    base_url: str
    username: str | None
    password: str | None
    timeout_s: float
    template_name: str
    index_name: str
    enabled: bool

    @classmethod
    def from_env(cls) -> OpenSearchBootstrap:
        base_url = (_env("OPENSEARCH_URL") or "http://127.0.0.1:9200").rstrip("/")
        username = _env("OPENSEARCH_USERNAME")
        password = _env("OPENSEARCH_PASSWORD")
        timeout_s = float(_env("OPENSEARCH_TIMEOUT_SECONDS", "10") or "10")

        enabled_raw = _env("OPENSEARCH_BOOTSTRAP_ENABLED", "false") or "false"
        enabled = enabled_raw.lower() in ("1", "true", "yes")

        default_index = "narralytica-videos-v1"
        index_name = _env("OPENSEARCH_VIDEOS_INDEX", default_index) or default_index

        default_template = "narralytica-videos-template-v1"
        template_name = (
            _env("OPENSEARCH_VIDEOS_TEMPLATE_NAME", default_template)
            or default_template
        )

        return cls(
            base_url=base_url,
            username=username,
            password=password,
            timeout_s=timeout_s,
            template_name=template_name,
            index_name=index_name,
            enabled=enabled,
        )

    def _auth(self):
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def bootstrap(self) -> None:
        if not self.enabled:
            return

        tmpl_path = Path(__file__).parent / "templates" / "videos-template-v1.json"

        if not tmpl_path.exists():
            body = {
                "index_patterns": [self.index_name],
                "template": {
                    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                    "mappings": {"properties": {"id": {"type": "keyword"}}},
                },
                "priority": 200,
                "version": 1,
            }
        else:
            body = json.loads(tmpl_path.read_text())

        base = self.base_url.rstrip("/")
        url = f"{base}/_index_template/{self.template_name}"

        with httpx.Client(timeout=self.timeout_s) as c:
            r = c.put(url, json=body, auth=self._auth())
            r.raise_for_status()

            idx_url = f"{base}/{self.index_name}"
            r2 = c.put(idx_url, json={}, auth=self._auth())
            if r2.status_code not in (200, 201, 400):
                r2.raise_for_status()
