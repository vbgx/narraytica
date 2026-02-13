from __future__ import annotations

from typing import Any

from services.infra.search_backends.opensearch.http import (
    opensearch_mget,
    opensearch_search,
)


def search(*, body: dict[str, Any]) -> dict[str, Any]:
    lexical, _sources, _scores, _hl = opensearch_search(body)

    hits = [{"_id": x["segment_id"], "_score": x["score"]} for x in lexical]
    return {"hits": {"hits": hits}}


def mget(*, ids: list[str]) -> dict[str, Any]:
    docs = []
    sources = opensearch_mget(ids)
    for sid in ids:
        if sid in sources:
            docs.append({"_id": sid, "found": True, "_source": sources[sid]})
        else:
            docs.append({"_id": sid, "found": False})
    return {"docs": docs}
