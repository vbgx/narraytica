import json
from pathlib import Path

from jsonschema import Draft202012Validator


def _find_repo_root(start: Path) -> Path:
    cur = start
    while True:
        candidate = cur / "packages" / "contracts" / "schemas" / "search.schema.json"
        if candidate.exists():
            return cur
        if cur.parent == cur:
            raise RuntimeError("Could not locate repo root.")
        cur = cur.parent


def test_search_response_matches_contract(client, monkeypatch):
    """
    Contract test:
    We mock search backends so this test validates
    ONLY API response structure against JSON Schema.
    """

    # --- Mock OpenSearch search ---
    def fake_opensearch_search(body):
        lexical = [{"segment_id": "seg_01", "score": 1.0}]
        sources = {
            "seg_01": {
                "video_id": "vid_01",
                "start_ms": 0,
                "end_ms": 1000,
                "text": "Hello world",
                "language": "en",
                "source": "youtube",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }
        lexical_scores = {"seg_01": 1.0}
        highlights = {"seg_01": [{"field": "text", "text": "<em>Hello</em> world"}]}
        return lexical, sources, lexical_scores, highlights

    def fake_mget(ids):
        return {}

    def fake_vector_search(*args, **kwargs):
        return []

    # Patch inside the route module
    import services.api.src.routes.search as search_module

    monkeypatch.setattr(search_module, "_opensearch_search", fake_opensearch_search)
    monkeypatch.setattr(search_module, "_opensearch_mget", fake_mget)
    monkeypatch.setattr(search_module, "vector_search", fake_vector_search)

    # --- Load contract schema ---
    here = Path(__file__).resolve()
    root = _find_repo_root(here)
    schema_path = root / "packages" / "contracts" / "schemas" / "search.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    # --- Call API ---
    resp = client.post(
        "/api/v1/search",
        json={
            "query": "hello",
            "mode": "hybrid",
            "limit": 5,
            "offset": 0,
        },
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()

    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    assert errors == [], "\n".join([f"{list(e.path)}: {e.message}" for e in errors])
