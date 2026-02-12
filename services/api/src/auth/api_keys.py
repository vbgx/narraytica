from __future__ import annotations

import hashlib


def hash_api_key(raw_api_key: str, pepper: str) -> str:
    raw = (raw_api_key or "").strip()
    if not raw:
        return ""
    material = (raw + pepper).encode("utf-8")
    return hashlib.sha256(material).hexdigest()
