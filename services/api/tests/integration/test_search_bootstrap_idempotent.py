import os

import pytest
from services.infra.search_backends.opensearch.bootstrap import OpenSearchBootstrap

pytestmark = pytest.mark.opensearch_integration

OS_URL = os.environ.get("OPENSEARCH_URL", "http://127.0.0.1:9200").rstrip("/")


def test_opensearch_bootstrap_is_idempotent():
    b = OpenSearchBootstrap(
        base_url=OS_URL,
        username=os.environ.get("OPENSEARCH_USERNAME"),
        password=os.environ.get("OPENSEARCH_PASSWORD"),
        timeout_s=10.0,
    )

    b.apply_segments_template_v1()
    b.apply_segments_template_v1()
