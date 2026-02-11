import os
import subprocess
import uuid

import pytest
from packages.shared.storage.s3_client import S3ObjectStorageClient


@pytest.fixture(scope="session")
def repo_root() -> str:
    return os.getenv("REPO_ROOT") or os.getcwd()


@pytest.fixture(scope="session")
def storage() -> S3ObjectStorageClient:
    endpoint = os.environ["S3_ENDPOINT"]
    access = os.environ["S3_ACCESS_KEY"]
    secret = os.environ["S3_SECRET_KEY"]
    return S3ObjectStorageClient(
        endpoint_url=endpoint, access_key=access, secret_key=secret
    )


@pytest.fixture(scope="session")
def database_url() -> str:
    return os.environ["DATABASE_URL"]


@pytest.fixture()
def test_ids() -> dict:
    u = uuid.uuid4().hex[:10]
    return {
        "video_id": f"video_it_{u}",
        "job_id": f"job_it_{u}",
    }


@pytest.fixture()
def temp_mp4(tmp_path) -> str:
    """
    Generate a small real MP4 with audio using ffmpeg.
    """
    out = tmp_path / "test.mp4"
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "testsrc=size=640x360:rate=30",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=1000",
        "-t",
        "2",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return str(out)
