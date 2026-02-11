# ADR — Architecture Decision Records

This folder contains **Architecture Decision Records (ADRs)** for the Narralytica platform.

ADRs capture **important technical decisions**, the context in which they were made, and the reasoning behind them.

They exist to prevent future confusion like:
> “Why did we choose this?”
> “Why is the system built this way?”

---

## 🎯 Purpose of ADRs

ADRs help:

- Preserve architectural intent
- Provide historical context
- Explain trade-offs and constraints
- Avoid repeating past debates

They are especially important in long-lived infrastructure systems like Narralytica.

---

## 🧱 When to Write an ADR

Create an ADR when making a decision that:

- Affects multiple services
- Impacts long-term scalability
- Involves major technology choices
- Changes core system behavior
- Is difficult or costly to reverse

Examples:
- Choosing a search stack (Qdrant + OpenSearch)
- Selecting orchestration tools
- Defining storage strategies

---

## 📄 ADR Format

Each ADR should include:

1. **Title** — Short and descriptive
2. **Status** — Proposed / Accepted / Deprecated
3. **Context** — Why the decision is needed
4. **Decision** — What was chosen
5. **Consequences** — Trade-offs and impacts

---

## 🔢 Naming Convention

Files should be numbered in order of creation:

0001-storage.md
0002-search-stack.md
0003-orchestration.md


Numbers are permanent and should not be reused.

---

## 🔄 Updating ADRs

ADRs are not rewritten after acceptance.
If a decision changes, create a **new ADR** referencing the old one.

---

## 🧠 Relationship with Other Docs

| Type | Purpose |
|------|---------|
| Architecture docs | Explain how the system is structured |
| Specs | Define system rules and contracts |
| Runbooks | Explain how to operate the system |
| ADRs | Explain why key decisions were made |

ADRs explain the **why**, not the **how**.
