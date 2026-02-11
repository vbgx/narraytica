#!/usr/bin/env bash
set -euo pipefail

QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"

COLLECTION="narralytica-segments-v1"
COLLECTION_FILE="infra/qdrant/collections/${COLLECTION}.collection.json"

echo "[qdrant] url=${QDRANT_URL}"

echo "[qdrant] wait for readyz..."
for i in {1..60}; do
  if curl -fsS "${QDRANT_URL}/readyz" >/dev/null; then
    break
  fi
  sleep 1
done

code="$(curl -sS -o /dev/null -w "%{http_code}" "${QDRANT_URL}/collections/${COLLECTION}")"
if [ "${code}" = "200" ]; then
  echo "[qdrant] collection exists: ${COLLECTION}"
else
  echo "[qdrant] create collection: ${COLLECTION}"
  curl -fsS -X PUT \
    "${QDRANT_URL}/collections/${COLLECTION}" \
    -H "Content-Type: application/json" \
    --data-binary @"${COLLECTION_FILE}" \
    >/dev/null
fi

echo "[qdrant] verify collection..."
curl -fsS "${QDRANT_URL}/collections/${COLLECTION}" >/dev/null
echo "[qdrant] done ✅"
