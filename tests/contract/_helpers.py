from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


def find_repo_root(start: Path | None = None) -> Path:
    cur = (start or Path(__file__).resolve()).resolve()
    for _ in range(80):
        if (cur / "packages").exists() and (cur / "tests").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RuntimeError("Could not locate repo root (expected /packages and /tests).")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as err:
        raise RuntimeError(f"Invalid JSON file: {path}") from err


def schemas_dir() -> Path:
    root = find_repo_root()
    d = root / "packages" / "contracts" / "schemas"
    if not d.exists():
        raise RuntimeError(f"Schemas dir not found: {d}")
    return d


def load_schema(schema_rel_path: str) -> dict[str, Any]:
    p = schemas_dir() / schema_rel_path
    if not p.exists():
        raise RuntimeError(f"Schema not found: {p}")
    return load_json(p)


def build_registry() -> Registry:
    """
    Build a registry containing ALL schemas in packages/contracts/schemas
    so relative $ref like "segment.schema.json" resolves.
    """
    reg: Registry = Registry()
    d = schemas_dir()

    for p in d.glob("*.json"):
        schema = load_json(p)

        # Provide both:
        # - the declared $id (preferred)
        # - the filename (for relative $ref like "segment.schema.json")
        resource = Resource.from_contents(schema, default_specification=DRAFT202012)

        schema_id = schema.get("$id")
        if isinstance(schema_id, str) and schema_id.strip():
            reg = reg.with_resource(schema_id, resource)

        reg = reg.with_resource(p.name, resource)

    return reg


_REGISTRY = build_registry()


@dataclass(frozen=True)
class ContractError:
    path: str
    message: str


def validate_payload(*, schema: dict[str, Any], payload: Any) -> None:
    validator = Draft202012Validator(schema, registry=_REGISTRY)
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    if not errors:
        return

    out: list[ContractError] = []
    for e in errors[:30]:
        p = ".".join(str(x) for x in e.path) if e.path else "$"
        out.append(ContractError(path=p, message=e.message))

    details = "\n".join(f"- {e.path}: {e.message}" for e in out)
    raise AssertionError(f"Contract validation failed:\n{details}")
