# Contracts Conventions — Narralytica

This folder defines canonical JSON Schemas for core entities and API payloads.

## Principles

- Schemas are the source of truth for payload shape and validation.
- IDs are stable opaque strings.
- Foreign keys are represented as string IDs (e.g. `video_id`, `segment_id`).
- Timestamps use `format: date-time` (RFC 3339 / ISO 8601).

## Compatibility rules

- Prefer additive changes.
- Avoid making previously optional fields required without a migration/version plan.
- Keep `additionalProperties: false` for core entities to prevent silent drift.

## Storage references

- Large artifacts are referenced via a canonical `storage_ref` object.
- Contract: `schemas/storage_ref.schema.json`.
