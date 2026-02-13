from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import jsonschema
except Exception as e:  # pragma: no cover
    jsonschema = None  # type: ignore[assignment]
    _jsonschema_import_error = e
else:
    _jsonschema_import_error = None


CONTRACTS_DIR = Path("packages/contracts")


@dataclass(frozen=True)
class SchemaRef:
    """
    Reference to a canonical schema inside packages/contracts.
    """

    relpath: str  # e.g. "schemas/search.schema.json"


class SchemaValidationError(ValueError):
    pass


def validate_against_schema(payload: Any, schema: SchemaRef) -> None:
    """
    Optional schema validation.
    - If jsonschema is not installed -> hard fail (better than silent drift).
    - If schema file missing -> hard fail (contracts must be explicit).
    """
    if jsonschema is None:  # pragma: no cover
        raise SchemaValidationError(
            "jsonschema is required for schema validation but is not installed: "
            f"{_jsonschema_import_error}"
        )

    schema_path = CONTRACTS_DIR / schema.relpath
    if not schema_path.exists():
        raise SchemaValidationError(f"Schema file not found: {schema_path}")

    schema_obj = _load_json(schema_path)
    try:
        jsonschema.validate(instance=payload, schema=schema_obj)
    except jsonschema.ValidationError as e:
        raise SchemaValidationError(str(e)) from e


def _load_json(path: Path) -> Any:
    import json

    return json.loads(path.read_text(encoding="utf-8"))
