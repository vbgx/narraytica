from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable

JsonObj = Mapping[str, Any]


class PersistencePortError(Exception):
    pass


class NotFound(PersistencePortError):
    pass


class Conflict(PersistencePortError):
    pass


class PreconditionFailed(PersistencePortError):
    pass


class RetryableError(PersistencePortError):
    pass


@runtime_checkable
class JobsRepoPort(Protocol):
    def create_job(self, job: JsonObj) -> JsonObj: ...
    def get_job(self, job_id: str) -> JsonObj: ...
    def create_job_run(self, job_run: JsonObj) -> JsonObj: ...
    def append_job_event(self, job_id: str, event: JsonObj) -> JsonObj: ...
    def list_job_runs(self, job_id: str) -> Sequence[JsonObj]: ...
    def list_job_events(self, job_id: str) -> Sequence[JsonObj]: ...


@runtime_checkable
class VideosRepoPort(Protocol):
    def upsert_video(self, video: JsonObj) -> JsonObj: ...
    def get_video(self, video_id: str) -> JsonObj: ...


@runtime_checkable
class SegmentsRepoPort(Protocol):
    def bulk_upsert_segments(self, segments: Sequence[JsonObj]) -> int: ...
    def list_segments_by_transcript(self, transcript_id: str) -> Sequence[JsonObj]: ...


@runtime_checkable
class TranscriptsRepoPort(Protocol):
    def create_transcript(self, transcript: JsonObj) -> JsonObj: ...
    def upsert_transcript(self, transcript: JsonObj) -> JsonObj: ...
    def get_transcript(self, transcript_id: str) -> JsonObj: ...


@runtime_checkable
class SpeakersRepoPort(Protocol):
    def upsert_speaker(self, speaker: JsonObj) -> JsonObj: ...
    def get_speaker(self, speaker_id: str) -> JsonObj: ...
