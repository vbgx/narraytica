#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(2)


def load_spec(path: Path) -> dict:
    if not path.exists():
        fail(f"Spec not found: {path}")

    if path.suffix.lower() == ".json":
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            fail(f"Invalid JSON: {e}")

    if path.suffix.lower() in {".yml", ".yaml"}:
        try:
            import yaml  # type: ignore
        except Exception:
            fail("PyYAML is required for YAML specs. Prefer using JSON spec in CI.")
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as e:
            fail(f"Invalid YAML: {e}")

    fail(f"Unsupported spec extension: {path.suffix}")


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: tools/scripts/openapi_validate.py <path/to/openapi.{json,yaml,yml}>"
        )
        raise SystemExit(2)

    path = Path(sys.argv[1]).resolve()
    spec = load_spec(path)

    openapi_ver = spec.get("openapi")
    if not isinstance(openapi_ver, str) or not openapi_ver.startswith("3."):
        fail(f"Missing/invalid 'openapi' version (expected 3.x): got {openapi_ver!r}")

    if "paths" not in spec or not isinstance(spec["paths"], dict):
        fail("Missing/invalid 'paths' object")

    print(f"OK: OpenAPI basic validation passed ({path})")


if __name__ == "__main__":
    main()
