from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import httpx

_TEMPLATE_NAME = "narralytica-segments-template-v1"


@dataclass(frozen=True)
class OpenSearchBootstrap:
    base_url: str
    username: str | None = None
    password: str | None = None
    timeout_s: float = 10.0

    def _auth(self):
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def apply_segments_template_v1(self) -> None:
        tmpl_path = Path(__file__).parent / "templates" / "segments-template-v1.json"
        body = json.loads(tmpl_path.read_text())

        base = self.base_url.rstrip("/")
        url = f"{base}/_index_template/{_TEMPLATE_NAME}"

        with httpx.Client(timeout=self.timeout_s) as c:
            r = c.put(url, json=body, auth=self._auth())
            r.raise_for_status()
