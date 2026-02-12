#!/usr/bin/env python3

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = ROOT / "tools" / "ci" / "dependency_boundaries_allowlist.yaml"
DRIFT_MAP = ROOT / "docs" / "architecture" / "drift-map.md"

RE_KEY = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*:\s*"(.*)"\s*$')
RE_START = re.compile(r"^\s*-\s*rule_id\s*:\s*([A-Z0-9_]+)\s*$")

REQ_KEYS = {
    "rule_id",
    "file",
    "import",
    "reason",
    "expires_on",
    "drift_map",
}


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(2)


def parse_date(s: str) -> date:
    y, m, d = map(int, s.split("-"))
    return date(y, m, d)


def main() -> int:
    if not ALLOWLIST.exists():
        fail(f"Allowlist not found: {ALLOWLIST}")

    if not DRIFT_MAP.exists():
        fail(f"Drift map not found: {DRIFT_MAP}")

    drift_text = DRIFT_MAP.read_text(encoding="utf-8")

    entries = []
    cur = None

    lines = ALLOWLIST.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        m0 = RE_START.match(line)
        if m0:
            if cur:
                entries.append(cur)
            cur = {"rule_id": m0.group(1), "__line__": i}
            continue

        if cur is None:
            fail(f"{ALLOWLIST}:{i}: content outside entry")

        m1 = RE_KEY.match(line)
        if m1:
            k, v = m1.group(1), m1.group(2)
            cur[k] = v

    if cur:
        entries.append(cur)

    errors = []

    for e in entries:
        line = e.get("__line__", "?")
        missing = sorted(REQ_KEYS - set(e.keys()))
        if missing:
            errors.append(f"{ALLOWLIST}:{line}: missing keys: {', '.join(missing)}")
            continue

        try:
            exp = parse_date(e["expires_on"])
            if exp < date.today():
                errors.append(
                    f"{ALLOWLIST}:{line}: expired "
                    f"allowlist entry ({e['drift_map']}) "
                    f"on {e['expires_on']}"
                )
        except Exception:
            errors.append(
                f"{ALLOWLIST}:{line}: invalid expires_on "
                f"format: {e.get('expires_on')!r}"
            )

        drift_id = e["drift_map"]
        if drift_id not in drift_text:
            errors.append(
                f"{ALLOWLIST}:{line}: drift_map id {drift_id} not found in {DRIFT_MAP}"
            )

    if errors:
        print("\n❌ allowlist policy violations:\n")
        for err in errors:
            print(" -", err)
        return 2

    print("✅ allowlist policy: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
