from __future__ import annotations

from pathlib import Path

from ._helpers import load_json, load_schema, validate_payload


def test_layer_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/layer_result.sample.json"))
    schema = load_schema("layer.schema.json")
    validate_payload(schema=schema, payload=payload)
