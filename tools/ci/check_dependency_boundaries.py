from __future__ import annotations

import ast
import fnmatch
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    paths: list[str]
    forbidden_imports: list[str]
    severity: str  # "error" | "warning"


@dataclass(frozen=True)
class AllowItem:
    rule_id: str
    file: str
    import_: str
    reason: str
    expires_on: str | None
    owner: str | None


@dataclass(frozen=True)
class Violation:
    rule_id: str
    severity: str
    file: str
    lineno: int
    import_: str
    message: str


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        raise RuntimeError(f"Missing config file: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _today_iso() -> str:
    return date.today().isoformat()


def _parse_date_iso(s: str) -> date:
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))


def _path_matches_any(rel: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, g) for g in globs)


def _import_matches_pattern(import_name: str, pattern: str) -> bool:
    # Pattern supports:
    # - exact: "fastapi"
    # - prefix: "services.api.src.search.*"
    if pattern.endswith(".*"):
        base = pattern[:-2]
        return import_name == base or import_name.startswith(f"{base}.")
    return import_name == pattern


def _read_allowlist(path: Path) -> list[AllowItem]:
    if not path.exists():
        return []

    raw = _load_yaml(path) or []
    out: list[AllowItem] = []

    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise RuntimeError(f"Allowlist item #{i} must be a mapping")

        expires_raw = item.get("expires_on")
        owner_raw = item.get("owner")

        expires_on = None
        if expires_raw:
            expires_on = str(expires_raw).strip()

        owner = None
        if owner_raw:
            owner = str(owner_raw).strip()

        out.append(
            AllowItem(
                rule_id=str(item.get("rule_id", "")).strip(),
                file=str(item.get("file", "")).strip(),
                import_=str(item.get("import", "")).strip(),
                reason=str(item.get("reason", "")).strip(),
                expires_on=expires_on,
                owner=owner,
            )
        )

    return out


def _fail_on_expired_allowlist(allow: list[AllowItem]) -> None:
    today = date.today()
    expired: list[AllowItem] = []

    for a in allow:
        if not a.expires_on:
            continue
        try:
            if _parse_date_iso(a.expires_on) < today:
                expired.append(a)
        except Exception as err:
            msg = (
                f"Allowlist has invalid expires_on date: {a.expires_on!r} "
                "(expected YYYY-MM-DD) "
                f"for rule_id={a.rule_id} file={a.file} import={a.import_}"
            )
            raise RuntimeError(msg) from err

    if expired:
        lines = ["Allowlist contains expired entries (CI must fail):"]
        for a in expired:
            lines.append(
                "  - "
                f"rule_id={a.rule_id} file={a.file} import={a.import_} "
                f"expires_on={a.expires_on} reason={a.reason}"
            )
        raise RuntimeError("\n".join(lines))


def _is_allowed(v: Violation, allow: list[AllowItem]) -> bool:
    for a in allow:
        if a.rule_id != v.rule_id:
            continue
        if not fnmatch.fnmatch(v.file, a.file):
            continue
        if _import_matches_pattern(v.import_, a.import_):
            return True
    return False


def _collect_imports(py: Path) -> list[tuple[int, str]]:
    """
    Returns list of (lineno, imported_module_string).
    Examples:
      import fastapi -> "fastapi"
      import fastapi.responses -> "fastapi.responses"
      from fastapi import HTTPException -> "fastapi"
      from services.api.src.search.engine import X -> "services.api.src.search.engine"
    """
    src = py.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src, filename=str(py))
    except SyntaxError:
        # If a file is invalid Python, linters already catch it.
        return []

    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append((node.lineno or 1, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.append((node.lineno or 1, node.module))
    return out


def _load_rules(config_path: Path) -> list[Rule]:
    raw = _load_yaml(config_path) or {}
    rules_raw = raw.get("rules", [])
    out: list[Rule] = []

    for r in rules_raw:
        out.append(
            Rule(
                id=str(r["id"]).strip(),
                description=str(r.get("description", "")).strip(),
                paths=list(r.get("paths", [])),
                forbidden_imports=list(r.get("forbidden_imports", [])),
                severity=str(r.get("severity", "error")).strip(),
            )
        )

    return out


def _iter_py_files(root: Path) -> list[Path]:
    ignored_dirnames = {
        ".git",
        ".venv",
        "node_modules",
        "dist",
        "build",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
    }

    out: list[Path] = []
    for p in root.rglob("*.py"):
        if set(p.parts) & ignored_dirnames:
            continue
        out.append(p)
    return out


def main(argv: list[str]) -> int:
    root = Path(".").resolve()
    config = Path("tools/ci/dependency_boundaries.yaml")
    allowlist = Path("tools/ci/dependency_boundaries_allowlist.yaml")

    it = iter(argv)
    for a in it:
        if a == "--root":
            root = Path(next(it)).resolve()
        elif a == "--config":
            config = Path(next(it)).resolve()
        elif a == "--allowlist":
            allowlist = Path(next(it)).resolve()
        else:
            print(f"Unknown arg: {a}", file=sys.stderr)
            return 2

    rules = _load_rules(config)
    allow = _read_allowlist(allowlist)
    _fail_on_expired_allowlist(allow)

    files = _iter_py_files(root)
    violations: list[Violation] = []

    for py in files:
        rel = py.relative_to(root).as_posix()

        applicable = [r for r in rules if _path_matches_any(rel, r.paths)]
        if not applicable:
            continue

        imports = _collect_imports(py)
        for lineno, mod in imports:
            for rule in applicable:
                for forbidden in rule.forbidden_imports:
                    if _import_matches_pattern(mod, forbidden):
                        v = Violation(
                            rule_id=rule.id,
                            severity=rule.severity,
                            file=rel,
                            lineno=lineno,
                            import_=forbidden,
                            message=f"Forbidden import '{mod}' (matched '{forbidden}')",
                        )
                        if _is_allowed(v, allow):
                            continue
                        violations.append(v)

    errors = [v for v in violations if v.severity.lower() == "error"]
    warnings = [v for v in violations if v.severity.lower() == "warning"]

    if warnings:
        print("Dependency boundary warnings:")
        for v in warnings:
            print(f"  [{v.rule_id}] {v.file}:{v.lineno} -> {v.message}")

    if errors:
        print("Dependency boundary errors:")
        for v in errors:
            print(f"  [{v.rule_id}] {v.file}:{v.lineno} -> {v.message}")
        print(f"\nAllowlist path: {allowlist.as_posix()}")
        print(f"Today: {_today_iso()}")
        return 1

    print("✅ dependency boundaries: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
