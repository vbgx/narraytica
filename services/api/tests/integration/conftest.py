from __future__ import annotations

import os

os.environ.setdefault("OPENSEARCH_URL", "http://localhost:9200")
os.environ.setdefault("OPENSEARCH_SEGMENTS_INDEX", "narralytica-segments-v1")

os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_SEGMENTS_COLLECTION", "narralytica-segments-v1")
