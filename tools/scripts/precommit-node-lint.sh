#!/usr/bin/env bash
set -euo pipefail

echo "[pre-commit][node] checking workspace…"

# No Node project at all → skip
if [[ ! -f "package.json" ]]; then
  echo "[pre-commit][node] skip (no package.json at repo root)"
  exit 0
fi

# pnpm not installed → skip (don’t block Python-only contributors)
if ! command -v pnpm >/dev/null 2>&1; then
  echo "[pre-commit][node] skip (pnpm not installed)"
  exit 0
fi

# No workspace file → treat as single project, still try lint if script exists
if [[ ! -f "pnpm-workspace.yaml" ]]; then
  if pnpm run | grep -q " lint"; then
    echo "[pre-commit][node] running: pnpm lint"
    pnpm lint
  else
    echo "[pre-commit][node] skip (no lint script in package.json)"
  fi
  exit 0
fi

# Workspace exists → run recursive lint
echo "[pre-commit][node] running: pnpm -r lint"
pnpm -r lint
