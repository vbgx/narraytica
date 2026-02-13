from packages.application.ports.persistence_ports import (
    JobsRepoPort,
    SegmentsRepoPort,
    SpeakersRepoPort,
    TranscriptsRepoPort,
    VideosRepoPort,
)


class FakeJobsRepo:
    def create_job(self, job):
        return job

    def get_job(self, job_id):
        return {"id": job_id}

    def create_job_run(self, job_run):
        return job_run

    def append_job_event(self, job_id, event):
        return event

    def list_job_runs(self, job_id):
        return []

    def list_job_events(self, job_id):
        return []


class FakeVideosRepo:
    def upsert_video(self, video):
        return video

    def get_video(self, video_id):
        return {"id": video_id}


class FakeSegmentsRepo:
    def bulk_upsert_segments(self, segments):
        return len(segments)

    def list_segments_by_transcript(self, transcript_id):
        return []


class FakeTranscriptsRepo:
    def create_transcript(self, transcript):
        return transcript

    def upsert_transcript(self, transcript):
        return transcript

    def get_transcript(self, transcript_id):
        return {"id": transcript_id}


class FakeSpeakersRepo:
    def upsert_speaker(self, speaker):
        return speaker

    def get_speaker(self, speaker_id):
        return {"id": speaker_id}


def test_ports_are_runtime_checkable():
    assert isinstance(FakeJobsRepo(), JobsRepoPort)
    assert isinstance(FakeVideosRepo(), VideosRepoPort)
    assert isinstance(FakeSegmentsRepo(), SegmentsRepoPort)
    assert isinstance(FakeTranscriptsRepo(), TranscriptsRepoPort)
    assert isinstance(FakeSpeakersRepo(), SpeakersRepoPort)
