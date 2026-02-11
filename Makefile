
# ----------------------------
# Docs quality
# ----------------------------
.PHONY: docs-lint docs-links docs-check

docs-lint:
	pnpm -s markdownlint-cli2 "**/*.md"

docs-links:
	node tools/scripts/docs-link-check.mjs

docs-check: docs-lint docs-links
	@echo "✅ docs-check OK"
