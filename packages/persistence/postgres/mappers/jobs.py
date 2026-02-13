from __future__ import annotations

from collections.abc import Mapping
from typing import Any

JsonObj = dict[str, Any]


def job_row_to_contract(row: Mapping[str, Any]) -> JsonObj:
    # Expect DB columns to match contract keys or be trivially mapped.
    return dict(row)


def job_run_row_to_contract(row: Mapping[str, Any]) -> JsonObj:
    return dict(row)


def job_event_row_to_contract(row: Mapping[str, Any]) -> JsonObj:
    return dict(row)
