from __future__ import annotations

from packages.search.engine import DefaultHybridMerger, SearchEngine
from packages.search.ranking import MergeWeights
from packages.search_infra.config import from_env
from packages.search_infra.opensearch_adapter import OpenSearchAdapter
from packages.search_infra.qdrant_adapter import QdrantAdapter
from services.api.src.search.qdrant.embeddings_client import embed_text


def build_search_engine() -> SearchEngine:
    cfg = from_env()

    os_adapter = OpenSearchAdapter(cfg=cfg.opensearch)

    qdrant_adapter = QdrantAdapter(
        cfg=cfg.qdrant,
        segment_store=os_adapter,
        embed_text=embed_text,
    )

    return SearchEngine(
        lexical=os_adapter,
        vector=qdrant_adapter,
        merger=DefaultHybridMerger(weights=MergeWeights(lexical=0.5, vector=0.5)),
    )
