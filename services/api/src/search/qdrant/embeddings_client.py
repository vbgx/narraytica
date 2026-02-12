from __future__ import annotations

import os
from dataclasses import dataclass

import requests


class EmbeddingsNotConfiguredError(RuntimeError):
    pass


@dataclass(frozen=True)
class EmbeddingsConfig:
    url: str
    model: str
    timeout_s: float
    vector_size: int


def load_embeddings_config() -> EmbeddingsConfig:
    url = (os.environ.get("EMBEDDINGS_URL") or "").strip()
    if not url:
        raise EmbeddingsNotConfiguredError(
            "Embeddings provider not configured: set EMBEDDINGS_URL"
        )

    model = (
        os.environ.get("EMBEDDING_MODEL") or "bge-large-en"
    ).strip() or "bge-large-en"

    timeout_s = float((os.environ.get("EMBEDDINGS_TIMEOUT_S") or "10").strip() or "10")

    vector_size = int(
        (os.environ.get("EMBEDDING_VECTOR_SIZE") or "1024").strip() or "1024"
    )

    return EmbeddingsConfig(
        url=url.rstrip("/"),
        model=model,
        timeout_s=timeout_s,
        vector_size=vector_size,
    )


def embed_text(query_text: str) -> list[float]:
    cfg = load_embeddings_config()
    text = (query_text or "").strip()
    if not text:
        raise ValueError("query_text is empty")

    payload = {"model": cfg.model, "texts": [text]}

    r = requests.post(
        f"{cfg.url}/embeddings",
        json=payload,
        timeout=cfg.timeout_s,
    )
    r.raise_for_status()
    data = r.json()

    vectors = data.get("vectors") or data.get("embeddings") or data.get("data")

    if isinstance(vectors, list) and vectors and isinstance(vectors[0], list):
        vec = vectors[0]
    elif (
        isinstance(vectors, list)
        and vectors
        and isinstance(vectors[0], dict)
        and "embedding" in vectors[0]
    ):
        vec = vectors[0]["embedding"]
    else:
        raise RuntimeError("invalid embeddings response shape")

    if not isinstance(vec, list):
        raise RuntimeError("embedding vector is not a list")

    if len(vec) != cfg.vector_size:
        got = len(vec)
        expected = cfg.vector_size
        raise RuntimeError(f"embedding dim mismatch: got={got} expected={expected}")

    return vec
