#!/usr/bin/env bash
set -euo pipefail

QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
COLLECTION="${1:-narralytica-segments-v1}"

curl -fsS "${QDRANT_URL}/readyz" >/dev/null
curl -fsS "${QDRANT_URL}/collections/${COLLECTION}" >/dev/null

echo "qdrant ok (collection=${COLLECTION})"
