# Documentation Style Guide — Narralytica

This guide defines the rules used to keep documentation **consistent, navigable, and agent-friendly**.

If a rule conflicts with an EPIC/CONTRACT/RUNBOOK template requirement, the template wins.

---

## Goals

- Make docs easy to scan and trustworthy.
- Prevent drift between docs, contracts, and code.
- Keep navigation stable across the repository.
- Enable automated checks (lint + link-check) and agent workflows.

---

## File Types and Expected Structure

### README.md (folder hub)
Use to explain:
- What this area contains
- What to read first
- How it connects to the rest of the system
- Quick “where to go next” links

Must include:
- Purpose
- Contents
- Navigation links (Back/Up/Next when relevant)

### RUNBOOK.md
Operational instructions for reruns, debugging, incidents.

Must include:
- When to use
- Step-by-step procedures
- Common failures
- Escalation
- Related docs

### CONTRACT.md
Formal interface contract: payloads, artifacts, guarantees.

Must include:
- Input payload schema (example JSON)
- Output artifacts
- State transitions
- Guarantees
- Non-responsibilities
- Related contracts

### EPIC (epics/epic-XX-*.md)
Project governance doc. Must match the standard EPIC template sections.

### ADR (docs/adr/*.md)
Decision record. Keep it short and factual:
- Context
- Decision
- Consequences

---

## Headings & Formatting

- Each document starts with a single `#` title.
- Use `##` for main sections, `###` for subsections.
- Keep paragraphs short (2–5 lines).
- Prefer lists and tables for scannability.
- Avoid duplicate headings at the same level in the same document.

---

## Links (Internal)

- Use **relative links only**.
- Prefer linking to files, not folders.
- Do not link to GitHub URLs for internal docs.
- Keep link targets stable (avoid renames).

Examples:
- `../README.md`
- `../../docs/architecture/pipelines.md`
- `./CONTRACT.md`

External links are allowed, but should be sparing and stable.

---

## Naming & Terminology

Use consistent terms:

- **video**: the source video entity
- **transcript**: full timecoded transcript artifact
- **segment**: time-bounded slice of speech
- **speaker**: speaker entity or cluster
- **layer**: AI enrichment output attached to a segment
- **job**: processing job tracked in the system
- **artifact**: stored output file or dataset produced by a step

Avoid inventing new names for existing concepts.

---

## Pagination & Navigation (Standard)

Use this standard nav format.

### Top of file (optional but recommended for leaf docs)
Place under the title:

- **Back**: the parent hub (folder README)
- **Up**: the closest index/hub above (often the same as Back)

Example:

Back: `../README.md`  
Up: `../../docs/README.md`

### Bottom of file (recommended for leaf docs)
Add a small navigation block:

---
Back: `../README.md` · Up: `../../docs/README.md`

If the doc is part of a linear sequence, add:

---
← Previous: `./previous.md` · Up: `../README.md` · Next: `./next.md`

Rules:
- “Up” should always point to a real hub doc (usually a README).
- Keep paths relative.
- Do not add Next/Previous unless there is a stable sequence.

---

## Do Not

- Do not delete required sections in EPIC/CONTRACT/RUNBOOK docs.
- Do not change file paths without a broader refactor plan.
- Do not add speculative claims (“will do X later”) unless it’s in an EPIC roadmap.
- Do not drift from contracts: schemas in `packages/contracts/` are the source of truth.

---

## Quality Checklist (per PR)

- All links are valid (relative links resolve)
- Doc titles match their folder purpose
- No duplicated concepts contradicting other docs
- Navigation exists where it adds value
- The change is small and reviewable (batching)
