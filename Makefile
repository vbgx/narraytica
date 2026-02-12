# ----------------------------
# Docs quality (disabled)
# ----------------------------
.PHONY: docs-check

docs-check:
	@echo "⚠️ docs checks disabled"

# ----------------------------
# Architecture guardrails (anti-drift)
# ----------------------------
.PHONY: ci-architecture

ci-architecture:
	uv run python tools/ci/check_dependency_boundaries.py \
		--root . \
		--config tools/ci/dependency_boundaries.yaml \
		--allowlist tools/ci/dependency_boundaries_allowlist.yaml
