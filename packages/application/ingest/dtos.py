from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IngestSourceDTO:
    kind: str
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"kind": self.kind}
        if self.url is not None:
            out["url"] = self.url
        return out


@dataclass(frozen=True)
class IngestRequestDTO:
    external_id: str | None
    source: IngestSourceDTO

    # optional future fields (keep for forward-compat, but do not require in HTTP)
    media: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    options: dict[str, Any] | None = None
    idempotency_key: str | None = None

    def to_payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"source": self.source.to_dict()}
        if self.external_id is not None:
            out["external_id"] = self.external_id
        if self.media is not None:
            out["media"] = self.media
        if self.metadata is not None:
            out["metadata"] = self.metadata
        if self.options is not None:
            out["options"] = self.options
        if self.idempotency_key is not None:
            out["idempotency_key"] = self.idempotency_key
        return out
