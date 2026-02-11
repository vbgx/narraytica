#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    print("ERROR: PyYAML is required (pip install pyyaml).", file=sys.stderr)
    sys.exit(2)


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"YAML parse failed for {path}: {e}")
    if not isinstance(data, dict):
        fail(f"OpenAPI root must be a mapping/object: {path}")
    return data


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"JSON parse failed for {path}: {e}")
    if not isinstance(data, dict):
        fail(f"JSON schema must be an object: {path}")
    return data


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: tools/scripts/openapi_validate.py <path/to/openapi.yaml>",
            file=sys.stderr,
        )
        sys.exit(2)

    spec_path = Path(sys.argv[1]).resolve()
    if not spec_path.exists():
        fail(f"Spec not found: {spec_path}")

    spec = load_yaml(spec_path)

    # Minimal structural checks (pragmatic)
    openapi_ver = spec.get("openapi")
    if not isinstance(openapi_ver, str) or not openapi_ver.startswith("3."):
        fail(f"Missing/invalid 'openapi' version (expected 3.x): got {openapi_ver!r}")

    if "paths" not in spec or not isinstance(spec["paths"], dict):
        fail("Missing/invalid 'paths' object")

    components = spec.get("components", {})
    if not isinstance(components, dict):
        fail("Invalid 'components' object")
    schemas = components.get("schemas", {})
    if not isinstance(schemas, dict):
        fail("Invalid 'components.schemas' object")

    # Validate referenced local schema files exist + are valid JSON
    base_dir = spec_path.parent
    for name, schema_def in schemas.items():
        if isinstance(schema_def, dict) and "$ref" in schema_def:
            ref = schema_def["$ref"]
            if not isinstance(ref, str):
                fail(f"components.schemas.{name} $ref must be string")
            # Only handle local file refs like ./schemas/foo.schema.json
            if ref.startswith("./") or ref.startswith("../"):
                target = (base_dir / ref).resolve()
                if not target.exists():
                    fail(f"Missing $ref target for schema '{name}': {ref} -> {target}")
                load_json(target)  # ensures valid JSON
            # else: ignore non-file refs (e.g., #/components/...)

    # Ensure every operation has responses (avoid undocumented shapes)
    paths = spec["paths"]
    for p, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, op in path_item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            if not isinstance(op, dict):
                fail(f"paths.{p}.{method} must be an object")
            if (
                "responses" not in op
                or not isinstance(op["responses"], dict)
                or len(op["responses"]) == 0
            ):
                fail(f"paths.{p}.{method} is missing responses")

    print(f"OK: OpenAPI basic validation passed ({spec_path})")


if __name__ == "__main__":
    main()
