# ============================================================
# Docs quality
# ============================================================

.PHONY: docs-check

docs-check:
	@echo "⚠️ docs checks disabled"


# ============================================================
# Contracts guardrails (anti-drift)
# ============================================================

.PHONY: ci-contracts

ci-contracts:
	python3 tools/ci/check_no_schema_duplication.py


# ============================================================
# OpenAPI guardrails (anti-drift)
# ============================================================

.PHONY: ci-openapi

OPENAPI_SPEC_JSON := packages/contracts/openapi.json

ci-openapi:
	@python3 -c "import json; json.load(open('$(OPENAPI_SPEC_JSON)', 'r', encoding='utf-8'))" >/dev/null
	python3 tools/scripts/openapi_validate.py $(OPENAPI_SPEC_JSON)


# ============================================================
# Allowlist policy (drift-map enforcement)
# ============================================================

.PHONY: ci-exceptions

ci-exceptions:
	python3 tools/ci/check_allowlist_policy.py


# ============================================================
# Contract tests
# ============================================================

.PHONY: test-contracts

test-contracts:
	uv run pytest -q tests/contract


# ============================================================
# Architecture guardrails (global anti-drift gate)
# ============================================================

.PHONY: ci-architecture

ci-architecture: ci-contracts ci-openapi ci-exceptions test-contracts
	uv run python tools/ci/check_dependency_boundaries.py \
		--root . \
		--config tools/ci/dependency_boundaries.yaml \
		--allowlist tools/ci/dependency_boundaries_allowlist.yaml
