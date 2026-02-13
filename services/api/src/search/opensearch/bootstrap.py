from __future__ import annotations

from services.infra.search_backends.opensearch.bootstrap import OpenSearchBootstrap


def bootstrap_opensearch() -> None:
    """
    Backward-compat shim for existing integration tests.
    """
    OpenSearchBootstrap.from_env().bootstrap()
