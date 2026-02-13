SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

OPENAPI_SPEC ?= packages/contracts/openapi.yaml

.PHONY: help \
	ci-architecture ci-exceptions test-contracts \
	check-schema-duplication check-openapi check-allowlist check-boundaries \
	py-lint py-format-check node-lint

help:
	@echo "Targets:"
	@echo "  make ci-architecture   # Phase 1+ gates"
	@echo "  make ci-exceptions     # allowlist policy checks"
	@echo "  make test-contracts    # contract tests only"
	@echo "  make check-boundaries  # dependency boundaries only"
	@echo "Variables:"
	@echo "  OPENAPI_SPEC=<path>    # default: $(OPENAPI_SPEC)"

ci-architecture: \
	check-schema-duplication \
	check-openapi \
	check-allowlist \
	test-contracts \
	check-boundaries

ci-exceptions: check-allowlist

test-contracts:
	pytest -q tests/contract

check-boundaries:
	uv run python tools/ci/check_dependency_boundaries.py \
	  --root . \
	  --config tools/ci/dependency_boundaries.yaml \
	  --allowlist tools/ci/dependency_boundaries_allowlist.yaml

check-schema-duplication:
	uv run python tools/ci/check_no_schema_duplication.py

check-openapi:
	if [[ ! -f "$(OPENAPI_SPEC)" ]]; then \
	  echo "ERROR: OPENAPI_SPEC not found: $(OPENAPI_SPEC)"; \
	  echo "Set it like: make check-openapi OPENAPI_SPEC=packages/contracts/openapi.yaml"; \
	  exit 2; \
	fi
	uv run python tools/scripts/openapi_validate.py "$(OPENAPI_SPEC)"

check-allowlist:
	uv run python tools/ci/check_allowlist_policy.py

py-lint:
	ruff check .

py-format-check:
	ruff format --check .

node-lint:
	pnpm -r lint
