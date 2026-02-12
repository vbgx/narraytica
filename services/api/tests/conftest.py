from __future__ import annotations

import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _repo_root() -> Path:
    """
    Find repo root by walking up until we see `services/` and `packages/`.
    """
    cur = Path(__file__).resolve()
    for p in [cur] + list(cur.parents):
        if (p / "services").exists() and (p / "packages").exists():
            return p
    raise RuntimeError("Could not locate repo root (expected services/ and packages/).")


@pytest.fixture(autouse=True, scope="session")
def _test_env_defaults() -> None:
    print("🚀 Setting test environment defaults...")

    os.environ.setdefault("OPENSEARCH_URL", "http://localhost:9200")
    os.environ.setdefault("OPENSEARCH_SEGMENTS_INDEX", "narralytica-segments-v1")

    os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
    os.environ.setdefault("QDRANT_SEGMENTS_COLLECTION", "narralytica-segments-v1")


def _import_app():
    root = _repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
        print(f"🧩 Added repo root to sys.path: {root}")

    print("🔍 Importing FastAPI app (package-aware)...")

    # This import keeps relative imports inside main.py working.
    from services.api.src.main import app  # type: ignore

    print("✅ Imported app from services.api.src.main")
    return app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app = _import_app()
    print("🧪 Creating TestClient...")
    with TestClient(app) as c:
        yield c
    print("🧹 TestClient closed.")
