import os

import pytest
from services.infra.search_backends.opensearch.bootstrap import OpenSearchBootstrap

pytestmark = pytest.mark.opensearch_integration

OS_URL = os.environ.get("OPENSEARCH_URL", "http://127.0.0.1:9200").rstrip("/")


def test_opensearch_bootstrap_is_idempotent():
    os.environ.setdefault("OPENSEARCH_URL", OS_URL)

    os.environ.setdefault("OPENSEARCH_BOOTSTRAP_ENABLED", "true")
    os.environ.setdefault("OPENSEARCH_TIMEOUT_SECONDS", "10")

    os.environ.setdefault("OPENSEARCH_VIDEOS_INDEX", "narralytica-it-segments-v1")
    os.environ.setdefault(
        "OPENSEARCH_VIDEOS_TEMPLATE_NAME",
        "narralytica-it-videos-template-v1",
    )

    b = OpenSearchBootstrap.from_env()

    b.bootstrap()
    b.bootstrap()
