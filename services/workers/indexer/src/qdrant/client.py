from __future__ import annotations

import requests


class QdrantClient:
    def __init__(
        self, base_url: str, api_key: str | None = None, timeout_s: float = 15.0
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["api-key"] = self.api_key
        return h

    def upsert_points(self, collection: str, points: list[dict]) -> None:
        if not points:
            return
        url = f"{self.base_url}/collections/{collection}/points?wait=true"
        payload = {"points": points}
        r = requests.put(
            url, json=payload, headers=self._headers(), timeout=self.timeout_s
        )
        r.raise_for_status()

    def count(self, collection: str) -> int:
        url = f"{self.base_url}/collections/{collection}/points/count"
        r = requests.post(
            url, json={"exact": False}, headers=self._headers(), timeout=self.timeout_s
        )
        r.raise_for_status()
        data = r.json()
        return int((data.get("result") or {}).get("count") or 0)
