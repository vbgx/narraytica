from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PKG_SEARCH = ROOT / "packages" / "search"
PKG_SEARCH_INFRA = ROOT / "packages" / "search_infra"
SERVICES = ROOT / "services"


FORBIDDEN_IMPORT_PREFIXES_IN_CORE = (
    "packages.search_infra",
    "requests",
    "opensearch",
    "qdrant",
    "qdrant_client",
)

ERRORS: list[str] = []


def is_python_file(p: Path) -> bool:
    return p.suffix == ".py"


def check_core_boundaries() -> None:
    """
    packages/search must stay pure.
    """
    for path in PKG_SEARCH.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if mod.startswith(FORBIDDEN_IMPORT_PREFIXES_IN_CORE):
                        ERRORS.append(
                            f"[CORE VIOLATION] {path.relative_to(ROOT)} "
                            f"imports forbidden module '{mod}'"
                        )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module
                    if mod.startswith(FORBIDDEN_IMPORT_PREFIXES_IN_CORE):
                        ERRORS.append(
                            f"[CORE VIOLATION] {path.relative_to(ROOT)} "
                            f"imports forbidden module '{mod}'"
                        )


def check_no_reverse_import() -> None:
    """
    Ensure packages/search does NOT import packages/search_infra.
    """
    for path in PKG_SEARCH.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("packages.search_infra"):
                    ERRORS.append(
                        f"[LAYER VIOLATION] {path.relative_to(ROOT)} "
                        f"must not depend on packages.search_infra"
                    )
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("packages.search_infra"):
                        ERRORS.append(
                            f"[LAYER VIOLATION] {path.relative_to(ROOT)} "
                            f"must not depend on packages.search_infra"
                        )


def main() -> None:
    if not PKG_SEARCH.exists():
        print("packages/search not found — skipping")
        sys.exit(0)

    check_core_boundaries()
    check_no_reverse_import()

    if ERRORS:
        print("\nSEARCH ARCHITECTURE BOUNDARY VIOLATIONS:\n")
        for e in ERRORS:
            print(" -", e)
        print("\nSearch core must remain pure.")
        sys.exit(1)

    print("Search boundaries check passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
