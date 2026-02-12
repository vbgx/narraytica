import os

import pytest
from packages.shared.storage.s3_client import S3ObjectStorageClient


@pytest.fixture(scope="session")
def database_url() -> str:
    # Same contract as ingest integration tests
    return os.environ["DATABASE_URL"]


@pytest.fixture(scope="session")
def storage() -> S3ObjectStorageClient:
    # Same contract as ingest integration tests
    return S3ObjectStorageClient(
        endpoint_url=os.environ.get("S3_ENDPOINT"),
        access_key=os.environ.get("S3_ACCESS_KEY"),
        secret_key=os.environ.get("S3_SECRET_KEY"),
        region=os.environ.get("S3_REGION", "us-east-1"),
    )
