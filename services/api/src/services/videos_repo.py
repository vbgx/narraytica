from __future__ import annotations

from datetime import UTC, datetime

from ..routes.videos import VideoListFilters, VideosRepo, VideoV1


class InMemoryVideosRepo(VideosRepo):
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self._items: list[VideoV1] = [
            VideoV1(video_id="vid_test_01", status="done", created_at=now),
            VideoV1(video_id="vid_test_02", status="queued", created_at=now),
        ]

    def list_videos(
        self,
        *,
        filters: VideoListFilters,
        limit: int,
        offset: int,
    ) -> tuple[list[VideoV1], int]:
        out = self._items

        if filters.status:
            out = [v for v in out if v.status == filters.status]

        if filters.created_after:
            out = [v for v in out if v.created_at > filters.created_after]

        if filters.created_before:
            out = [v for v in out if v.created_at < filters.created_before]

        total = len(out)
        return out[offset : offset + limit], total

    def get_video(self, *, video_id: str) -> VideoV1 | None:
        for v in self._items:
            if v.video_id == video_id:
                return v
        return None


_repo = InMemoryVideosRepo()


def get_repo() -> VideosRepo:
    return _repo
