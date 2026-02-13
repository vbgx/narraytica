from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

_CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "contracts"


def _load_schema(filename: str) -> dict[str, Any]:
    p = _CONTRACTS_DIR / filename
    if not p.exists():
        raise RuntimeError(f"contract schema not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def validate_against(schema_filename: str, payload: dict[str, Any]) -> None:
    """
    Raises ValueError with a stable error message if invalid.
    """
    schema = _load_schema(schema_filename)
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(payload), key=lambda e: e.json_path)
    if not errors:
        return
    first = errors[0]
    msg = first.message
    path = first.json_path or "$"
    raise ValueError(f"{schema_filename}: {path}: {msg}")
