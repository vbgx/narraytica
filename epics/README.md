# EPICs — Narralytica

This folder is the **source of truth** for delivery planning.

- Each EPIC is a **scope boundary** with explicit outcomes.
- EPICs map 1:1 to a set of GitHub Issues (numbered `XX.YY`).
- Docs live under `/docs`, and must be linked from EPICs to avoid drift.

## Naming

- EPIC files: `epic-XX-<slug>.md`
- GitHub issues: `XX.YY — <short title>`
  - `XX` = EPIC number
  - `YY` = issue number inside the EPIC

Examples:
- `EPIC 03 — Transcription & Segmentation`
  - `03.01 — Integrate ASR provider`
  - `03.02 — Implement timecoded segmenter`

## Required EPIC structure

Every EPIC file must contain:

- Goal
- Scope
- Non-goals
- Deliverables
- Issues (numbered list)
- Definition of Done
- Risks / Mitigations
- Links (docs/specs/runbooks/ADR)

Use `epic-template.md`.

## How to work day-to-day

1. Pick the next EPIC from `roadmap.md`
2. Create the GitHub issues with the same `XX.YY` numbering
3. Implement in small PRs
4. Update the EPIC “Definition of Done” checklist as you progress
5. Keep docs up to date (or open a docs issue in the same EPIC)

## Definition of Done (global)

A work item is considered done when:

- Code is merged (reviewed)
- Tests pass (unit/integration as applicable)
- Migrations are applied (if DB changes)
- Contracts are updated (if API/data changes)
- Runbook is updated (if operations change)
- Relevant docs are linked from the EPIC (no orphan decisions)
