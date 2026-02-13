from __future__ import annotations

from services.api.src.wiring.search_deps import build_search_deps


def build_engine():
    return build_search_deps
