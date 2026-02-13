from __future__ import annotations

from pathlib import Path

API_DOMAIN_DIR = Path("services/api/src/domain")


def main() -> int:
    """
    Fail if services/api/src/domain grows (anti-drift).
    """
    if not API_DOMAIN_DIR.exists():
        return 0

    # Keep it strict: any file presence means "domain logic lives in API"
    files = [p for p in API_DOMAIN_DIR.rglob("*") if p.is_file()]
    if files:
        rel = [str(p) for p in sorted(files)]
        print("ERROR: services/api/src/domain must not contain domain logic.")
        print("Found files:")
        for p in rel:
            print(f"- {p}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
