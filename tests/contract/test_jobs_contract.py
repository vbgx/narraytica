from __future__ import annotations

from pathlib import Path

from ._helpers import load_json, load_schema, validate_payload


def test_job_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/job.min.json"))
    schema = load_schema("job.schema.json")
    validate_payload(schema=schema, payload=payload)


def test_job_run_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/job_run.min.json"))
    schema = load_schema("job_run.schema.json")
    validate_payload(schema=schema, payload=payload)


def test_job_event_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/job_event.sample.json"))
    schema = load_schema("job_event.schema.json")
    validate_payload(schema=schema, payload=payload)
