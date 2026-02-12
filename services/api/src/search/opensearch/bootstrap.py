from pathlib import Path

# Repo root derived from this file location (deterministic, no CWD dependency).
REPO_ROOT = Path(__file__).resolve().parents[6]

TEMPLATE_PATH = (
    REPO_ROOT
    / "infra"
    / "opensearch"
    / "templates"
    / "narralytica-videos-v1.template.json"
)


def load_template() -> dict:
    import json

    with TEMPLATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
