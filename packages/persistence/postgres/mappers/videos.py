from __future__ import annotations

from collections.abc import Mapping
from typing import Any

JsonObj = dict[str, Any]


def video_row_to_contract(row: Mapping[str, Any]) -> JsonObj:
    return dict(row)
