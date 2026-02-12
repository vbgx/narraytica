from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class IngestionJobPayload(BaseModel):
    type: Literal["video_ingestion"] = "video_ingestion"
    version: str = Field(default="2.0")
    video_id: str

    source: dict[str, Any]
    dedupe: dict[str, Any]
    artifacts: dict[str, Any]
    metadata: dict[str, Any] | None = None
