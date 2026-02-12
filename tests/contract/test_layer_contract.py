import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "packages" / "contracts" / "schemas"
FIXTURE = ROOT / "tests" / "fixtures" / "contracts" / "layer_result.sample.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_registry() -> Registry:
    reg = Registry()
    for schema_path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        schema = load_json(schema_path)
        res = Resource.from_contents(schema)
        reg = reg.with_resource(schema_path.name, res)
        schema_id = schema.get("$id")
        if isinstance(schema_id, str) and schema_id:
            reg = reg.with_resource(schema_id, res)
    return reg


def test_layer_fixture_matches_envelope_contract():
    schema = load_json(SCHEMAS_DIR / "layer_envelope.schema.json")
    Draft202012Validator.check_schema(schema)
    instance = load_json(FIXTURE)
    Draft202012Validator(schema, registry=build_registry()).validate(instance)
