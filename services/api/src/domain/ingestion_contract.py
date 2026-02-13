from __future__ import annotations

from packages.domain.ingest.contracts import (
    IngestOptions,
    IngestRequest,
    IngestSource,
)

"""
DEPRECATED WRAPPER.

This module delegates to packages.domain.ingest.contracts.
It exists only for backward compatibility and will be removed in Phase 7.
"""

__all__ = [
    "IngestRequest",
    "IngestSource",
    "IngestOptions",
]
