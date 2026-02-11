# Specifications — Narralytica System Rules

This folder contains **system-wide technical specifications**.

Specs define **how Narralytica must behave**, independent of any specific implementation.  
They are the **rules of the platform**.

If architecture explains *structure* and runbooks explain *operations*,  
**specs define contracts and invariants**.

---

## 🎯 Purpose

Specifications exist to ensure:

- Consistency across services
- Predictable API behavior
- Clear security and permission boundaries
- Stable event and job contracts

They help prevent drift between components.

---

## 📚 Available Specifications

| File | Purpose |
|------|---------|
| `events.md` | Event bus structure and job lifecycle events |
| `permissions.md` | Roles, scopes, and access control model |
| `rate-limits.md` | API rate limiting strategy and enforcement |

---

## 🧱 What Belongs in a Spec

A document belongs here if it defines:

- A **platform-wide rule**
- A **contract between services**
- A **security or access model**
- A **non-negotiable system invariant**

Specs should not contain:
- Implementation details
- Operational procedures
- Architecture diagrams

---

## 🔄 Relationship with Code

When code changes affect a specification:

1. The spec must be updated first or in the same PR
2. Related services must be aligned
3. Contracts in `/packages/contracts` must remain consistent

Specs and contracts must never contradict each other.

---

## 🧠 Relationship with EPICs

Every EPIC that affects system behavior should link to:

- Relevant specs in this folder
- Updated contracts in `/packages/contracts`

An EPIC is not complete if it changes behavior without updating specs.

---

## ⚖️ Stability

Specifications are expected to change slowly.  
Frequent changes to specs may indicate unstable platform boundaries.
