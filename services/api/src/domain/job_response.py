"""
DEPRECATED — moved to packages.application.jobs.normalizers
"""

from packages.application.jobs.normalizers import (
    normalize_job,
    normalize_job_event,
    normalize_job_run,
)

__all__ = [
    "normalize_job",
    "normalize_job_event",
    "normalize_job_run",
]
