#!/usr/bin/env python3

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ALLOWED_SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas"

WHITELIST_DIRS = [
    ROOT / "infra" / "opensearch" / "templates",
    ROOT / "infra" / "qdrant" / "collections",
    ROOT / "packages" / "search" / "opensearch",
    ROOT / "packages" / "search" / "qdrant",
    ROOT / "tests" / "fixtures",
]

EXCLUDED_DIR_NAMES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    ".direnv",
    "__pycache__",
    "dist",
    "build",
}

SCHEMA_KEYS = {
    "$schema",
    "properties",
    "required",
    "oneOf",
    "allOf",
    "anyOf",
    "definitions",
    "additionalProperties",
}


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts)


def is_whitelisted(path: Path) -> bool:
    for allowed in WHITELIST_DIRS:
        if allowed in path.parents:
            return True
    return False


def looks_like_schema(data) -> bool:
    return isinstance(data, dict) and any(k in data for k in SCHEMA_KEYS)


def main() -> int:
    errors: list[str] = []

    for json_file in ROOT.rglob("*.json"):
        if is_excluded(json_file):
            continue

        if ALLOWED_SCHEMA_ROOT in json_file.parents:
            continue

        if is_whitelisted(json_file):
            continue

        if json_file.name.endswith(".schema.json"):
            errors.append(f"Forbidden schema file outside contracts: {json_file}")
            continue

        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        if looks_like_schema(data):
            errors.append(f"Schema-like JSON detected outside contracts: {json_file}")

    if errors:
        print("\n❌ JSON Schema duplication detected:\n")
        for e in errors:
            print(" -", e)
        return 1

    print("✅ No schema duplication detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
