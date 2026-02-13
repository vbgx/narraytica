from __future__ import annotations

import os

import requests


class EmbeddingsNotConfiguredError(RuntimeError):
    pass


def embed_text(text: str) -> list[float]:
    url = os.environ.get("EMBEDDINGS_URL")
    if not url:
        raise EmbeddingsNotConfiguredError("Embeddings provider not configured")

    r = requests.post(url, json={"text": text}, timeout=10)
    r.raise_for_status()
    data = r.json()
    vec = data.get("embedding") or data.get("vector")
    if not isinstance(vec, list):
        raise RuntimeError("invalid embeddings response")
    return [float(x) for x in vec]
