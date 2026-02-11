# EPIC 10 — Testing & Quality

## 🎯 Goal

Establish a robust testing strategy to ensure **reliability, correctness, and regression safety** across Narralytica’s pipelines, APIs, and search system.

This EPIC makes the platform **safe to evolve**.

---

## 📦 Scope

This EPIC includes:

- Unit testing across services and workers  
- Integration testing for end-to-end pipelines  
- Contract testing for API and schemas  
- Search relevance smoke tests  
- Load testing for core endpoints  
- CI integration for automated validation  

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Full-scale production stress testing  
- UI testing for end-user apps  
- Business KPI analytics validation  

It focuses on **technical correctness and stability**.

---

## 🧱 Testing Layers

| Layer | Purpose |
|------|---------|
| Unit tests | Validate small logic units |
| Integration tests | Validate service interactions |
| Contract tests | Ensure API/schema consistency |
| Search tests | Validate retrieval quality |
| Load tests | Measure system limits |

---

## 🗂 Deliverables

- Test frameworks configured across repos  
- CI workflows running tests automatically  
- Integration test environment via Docker Compose  
- Contract tests validating OpenAPI and JSON schemas  
- Search smoke test suite  
- Load test scripts for API and search  

---

## 🗂 Issues

1. Set up test framework for API service  
2. Add unit tests for domain logic  
3. Add unit tests for workers  
4. Build integration test environment  
5. Implement end-to-end pipeline test  
6. Implement contract validation tests  
7. Create search relevance smoke tests  
8. Add load testing scripts  
9. Integrate tests into CI  
10. Enforce test coverage thresholds  
11. Document testing strategy  
12. Create troubleshooting guide for failing tests  

---

## ✅ Definition of Done

EPIC 10 is complete when:

- All services have unit tests  
- Pipelines can be tested end-to-end locally  
- API contracts are automatically validated  
- Search queries have smoke tests  
- CI fails on test regressions  
- Documentation explains how to run tests  

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Slow test suite | Separate fast vs heavy tests |
| Flaky integration tests | Use deterministic fixtures |
| Schema drift | Enforce contract tests in CI |
| Low test adoption | Make tests part of DoD |

---

## 🔗 Links

- Test structure → `tests/`  
- Contracts → `packages/contracts/`  
- Runbooks → `docs/runbooks/local-dev.md`
