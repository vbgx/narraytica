from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class SearchFiltersV1(BaseModel):
    language: str | None = Field(default=None)
    source: str | None = Field(default=None)
    video_id: str | None = Field(default=None)
    speaker_id: str | None = Field(default=None)

    date_from: str | None = Field(default=None, description="RFC3339 date-time")
    date_to: str | None = Field(default=None, description="RFC3339 date-time")

    @field_validator("language", "source", "video_id", "speaker_id", mode="before")
    @classmethod
    def _empty_to_none(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("date_from", "date_to")
    @classmethod
    def _validate_rfc3339(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            return None
        try:
            datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception as e:
            raise ValueError("invalid RFC3339 date-time") from e
        return s

    @model_validator(mode="after")
    def _validate_range(self) -> SearchFiltersV1:
        if self.date_from and self.date_to:
            a = datetime.fromisoformat(self.date_from.replace("Z", "+00:00"))
            b = datetime.fromisoformat(self.date_to.replace("Z", "+00:00"))
            if b <= a:
                raise ValueError("date_to must be > date_from")
        return self

    def to_opensearch_filters(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []

        if self.language:
            out.append({"term": {"language": self.language}})
        if self.source:
            out.append({"term": {"source": self.source}})
        if self.video_id:
            out.append({"term": {"video_id": self.video_id}})
        if self.speaker_id:
            out.append({"term": {"speaker_id": self.speaker_id}})

        if self.date_from or self.date_to:
            r: dict[str, Any] = {}
            if self.date_from:
                r["gte"] = self.date_from
            if self.date_to:
                r["lt"] = self.date_to
            out.append({"range": {"created_at": r}})

        return out

    def to_qdrant_filter(self) -> dict[str, Any] | None:
        must: list[dict[str, Any]] = []

        def term(key: str, value: str | None) -> None:
            if value is None:
                return
            must.append({"key": key, "match": {"value": value}})

        term("language", self.language)
        term("source", self.source)
        term("video_id", self.video_id)
        term("speaker_id", self.speaker_id)

        if self.date_from or self.date_to:
            gte = None
            lt = None
            if self.date_from:
                gte = _to_epoch_ms(self.date_from)
            if self.date_to:
                lt = _to_epoch_ms(self.date_to)

            rr: dict[str, Any] = {}
            if gte is not None:
                rr["gte"] = gte
            if lt is not None:
                rr["lt"] = lt

            must.append({"key": "created_at_ms", "range": rr})

        if not must:
            return None

        return {"must": must}


def _to_epoch_ms(dt: str) -> int:
    d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=UTC)
    return int(d.timestamp() * 1000)
