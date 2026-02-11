# Contracts Changelog

This file tracks notable changes to cross-boundary contracts.

Contracts include:

API request/response shapes

Error model formats and error codes

Event envelope and payload schemas

Dataset formats used by pipelines

Search document schemas exposed across packages/services

Any shared types that other components depend on

This changelog exists to prevent silent drift and to make contract evolution auditable.

[Unreleased]
Added
Changed
Deprecated
Removed
Fixed
Security
Versioning Policy

Additive changes should not break consumers.

Breaking changes require explicit versioning and migration notes.

Events must bump version when payload changes incompatibly.

API changes should prefer additive evolution; endpoint versioning is a last resort.

See also:

packages/contracts/conventions.md

docs/specs/events.md

services/api/ERROR_MODEL.md

services/api/RATE_LIMITS.md

Entry Format

When adding an entry, include:

Contract area (API / Events / Schemas / Search / Datasets)

What changed

Impact (who must update)

Migration / rollout notes (if needed)

Version bump (if applicable)

Example:

### Changed
- [Events] ai.enrichment_completed v1 → v2: added `model` and changed `tokens` to an object.
  Impact: workers consuming enrichment events must handle v2.
  Migration: support v1+v2 for 2 releases, then drop v1.

Release Notes Discipline

Update this file whenever a PR changes a contract.

If the PR is internal-only but affects another package/service, it still belongs here.

Do not “rewrite history”: append new entries rather than altering past releases.

End of Contracts Changelog
