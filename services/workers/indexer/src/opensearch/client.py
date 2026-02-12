from __future__ import annotations

import json
from collections.abc import Iterable

import requests


class OpenSearchClient:
    def __init__(
        self,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        timeout_s: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password) if username and password else None
        self.timeout_s = timeout_s

    def bulk_upsert(
        self, index: str, docs: Iterable[dict], id_field: str = "id"
    ) -> None:
        lines: list[str] = []
        for d in docs:
            _id = d.get(id_field)
            if not _id:
                raise ValueError(f"missing id field '{id_field}' in doc")
            action = {"update": {"_index": index, "_id": str(_id)}}
            body = {"doc": d, "doc_as_upsert": True}
            lines.append(json.dumps(action, ensure_ascii=False))
            lines.append(json.dumps(body, ensure_ascii=False))

        if not lines:
            return

        payload = "\n".join(lines) + "\n"
        url = f"{self.base_url}/_bulk"
        headers = {"Content-Type": "application/x-ndjson"}
        r = requests.post(
            url,
            data=payload.encode("utf-8"),
            headers=headers,
            auth=self.auth,
            timeout=self.timeout_s,
        )
        r.raise_for_status()
        out = r.json()
        if out.get("errors"):
            items = out.get("items") or []
            sample_err = None
            for it in items:
                if isinstance(it, dict):
                    u = it.get("update") or it.get("index") or it.get("create")
                    if isinstance(u, dict) and u.get("error"):
                        sample_err = u["error"]
                        break
            raise RuntimeError(f"opensearch bulk had errors: sample={sample_err}")

    def refresh(self, index: str) -> None:
        url = f"{self.base_url}/{index}/_refresh"
        r = requests.post(url, auth=self.auth, timeout=self.timeout_s)
        r.raise_for_status()
