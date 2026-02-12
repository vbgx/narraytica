import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "packages" / "contracts" / "schemas"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "contracts"

FIXTURE_TO_SCHEMA = {
    "search_result.sample.json": "search.schema.json",
    "job.min.json": "job.schema.json",
    "job_event.sample.json": "job_event.schema.json",
    "job_run.min.json": "job_run.schema.json",
    "video.min.json": "video.schema.json",
    "transcript.min.json": "transcript.schema.json",
    "segment.min.json": "segment.schema.json",
    "speaker.min.json": "speaker.schema.json",
    "layer_result.sample.json": "layer_envelope.schema.json",
}

REQUIRED_COVERAGE = {
    "search": ["search.schema.json"],
    "jobs": [
        "job.schema.json",
        "job_event.schema.json",
        "job_run.schema.json",
    ],
    "entities": [
        "video.schema.json",
        "transcript.schema.json",
        "segment.schema.json",
        "speaker.schema.json",
    ],
    "layer": ["layer_envelope.schema.json"],
}


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


REGISTRY = build_registry()


def validator_for(schema_name: str) -> Draft202012Validator:
    schema_path = SCHEMAS_DIR / schema_name
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, registry=REGISTRY)


def test_required_schemas_exist():
    missing = []
    for group, names in REQUIRED_COVERAGE.items():
        for name in names:
            if not (SCHEMAS_DIR / name).exists():
                missing.append(f"{group}: {name}")

    assert not missing, "Missing required schemas:\n" + "\n".join(missing)


def test_all_schemas_are_valid_jsonschema():
    for schema_path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize(
    "fixture_name,schema_name",
    sorted(FIXTURE_TO_SCHEMA.items()),
)
def test_fixture_validates_against_schema(
    fixture_name: str,
    schema_name: str,
):
    fixture_path = FIXTURES_DIR / fixture_name
    assert fixture_path.exists(), f"Missing fixture: {fixture_path}"

    instance = load_json(fixture_path)
    validator_for(schema_name).validate(instance)
