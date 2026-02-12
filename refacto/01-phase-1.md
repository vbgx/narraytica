# PHASE 1 — Anti-drift guardrails (fondation CI) — Milestone REFACTO

Objectif
Rendre le drift détectable par CI avant tout déplacement de code : dépendances, contrats, duplication de schémas, et une cartographie des zones à risque.

Principe de phase
On ne “refacto” pas encore la logique : on met des barrières qui empêchent d’empirer et qui révèlent où ça dérive.

## Issue 1.1 — CI: Dependency boundaries (import rules anti-drift)

Title: ci(architecture): add dependency boundaries check (anti-drift)
Labels: ci, architecture, drift, refactor
Priority: P0 (bloquant)

Objectif

CI échoue si services/api ou un worker importe :

de l’IO infra au mauvais endroit (DB/OpenSearch/Qdrant),

du HTTP dans packages/*,

ou du code “métier” qui devrait vivre dans packages/*.

Scope exact

Appliquer des règles sur :

packages/**

services/api/src/**

services/workers/**/src/**

tests/** (souvent source de drift aussi, au moins en warning)

Règles v1 (minimales mais fortes)

R1 — No HTTP in packages

Interdit dans packages/** : fastapi, starlette, uvicorn, HTTPException, Request, Response

R2 — Routes are glue

Interdit dans services/api/src/routes/** : imports directs de clients infra :

Postgres driver/ORM (psycopg, asyncpg, sqlalchemy)

OpenSearch (opensearch, elasticsearch)

Qdrant (qdrant_client)

Interdit aussi : imports de modules “search impl” internes à l’API (si encore existants) hors wiring.

R3 — Workers don’t own clients (progressif)

Interdit dans services/workers/**/src/** : clients DB/search locaux sauf si explicitement allowlisté (au début).

R4 — Single source of behavior (guardrail)

Interdire l’import de services/api/src/search/** depuis routes (si ce répertoire existe encore), pour forcer l’évolution vers packages/search.

Mécanique (implémentation recommandée)

Script Python AST (robuste) + config YAML :

tools/ci/check_dependency_boundaries.py

tools/ci/dependency_boundaries.yaml

Allowlist obligatoire et horodatée :

tools/ci/dependency_boundaries_allowlist.yaml

Format allowlist (exigé)

rule_id

file (glob ou chemin)

import (module interdit)

reason

expires_on (YYYY-MM-DD)

owner (optionnel, mais utile)

Steps (checklist)

 Créer tools/ci/check_dependency_boundaries.py (parse AST, récupère import/from import)

 Créer tools/ci/dependency_boundaries.yaml (déclare rulesets par path)

 Créer tools/ci/dependency_boundaries_allowlist.yaml (vide au départ si possible)

 Ajouter make ci-architecture (ou équivalent) qui exécute ce check

 Brancher dans CI (même job que lint/typecheck si possible)

 Ajouter doc courte docs/architecture/rules.md (règles + comment demander exception)

 Ajouter règle “allowlist expired fails CI” (si expires_on < today)

DoD

CI échoue si packages/** importe FastAPI/HTTPException/etc.

CI échoue si une route importe un client DB/search.

CI échoue si allowlist contient une entrée expirée.

CI est stable (pas de faux positifs sur stdlib / imports relatifs).

Risques & mitigation

Faux positifs (imports indirects, alias)
→ AST + allowlist ciblée, et itération v1/v2.

Trop strict trop tôt
→ commencer par “denylist IO/HTTP” seulement, puis étendre.

## Issue 1.2 — Contract tests: couvrir payloads clés (request+response)

Title: tests(contracts): extend contract tests for core payloads (search/jobs/segments/transcripts/videos)
Labels: tests, contracts, drift
Priority: P0

Objectif

Chaque payload public critique (API responses, events workers) doit être validable contre les JSON Schemas canoniques.

Scope exact

Étendre tests/contract/* pour couvrir au minimum :

Search

SearchQuery (request)

SearchResult (response)

Ingestion / Core entities

Video

Segment

Transcript

Speaker

Jobs / runtime

Job

JobRun

JobEvent

AI layers

LayerResult (envelope, même si payload permissif v0)

Approche recommandée (pour éviter du drift dans les tests)

Un helper unique tests/contract/_helpers.py :

charge un schema depuis packages/contracts/schemas/**

valide un JSON payload (jsonschema)

Payloads de test versionnés et lisibles :

tests/fixtures/contracts/*.json (ou tools/fixtures/…)

Steps (checklist)

 Ajouter tests/contract/_helpers.py (load schema, validate, nice errors)

 Ajouter fixtures minimales :

tests/fixtures/contracts/search_query.min.json

tests/fixtures/contracts/search_result.min.json

tests/fixtures/contracts/segment.min.json

tests/fixtures/contracts/transcript.min.json

tests/fixtures/contracts/job_event.min.json

tests/fixtures/contracts/layer_result.min.json

 Ajouter tests :

tests/contract/test_search_contract.py

tests/contract/test_entities_contract.py (video/segment/transcript/speaker)

tests/contract/test_jobs_contract.py

tests/contract/test_layer_contract.py

 Ajouter au moins 1 fixture “semi-réaliste” (pas juste minimal) pour Search et JobEvent

DoD

Tous les tests contract passent en CI.

Chaque endpoint principal a au moins 1 couple request/response validé (même si via fixtures).

Les tests échouent avec messages explicites (path du champ, schema, etc.).

Risques & mitigation

Schemas incomplets / trop stricts
→ c’est un signal : soit corriger schema (source of truth), soit corriger code.

Tests trop artificiels
→ ajouter 1 payload “réaliste” dérivé d’un exemple E2E.

Issue 1.3 — CI: No schema duplication (single source of truth)

Title: ci(contracts): forbid JSON Schema duplication outside packages/contracts/schemas
Labels: ci, contracts, drift
Priority: P0

Objectif

Empêcher toute création de “schémas parallèles” ailleurs dans le repo.

Scope exact

Détecter :

fichiers *.schema.json

ou fichiers JSON contenant marqueurs JSON Schema ($schema, properties, required, type, oneOf, etc.)

Autorisé

packages/contracts/schemas/**

Autorisé (exceptions explicites)

Templates OpenSearch / mappings / settings (ex: infra/opensearch/**, packages/search/adapters/**/templates/**)
→ on les whiteliste précisément, sinon c’est la porte ouverte.

Steps (checklist)

 Script tools/ci/check_no_schema_duplication.py

 Règles :

scan glob **/*.json + heuristique “looks like jsonschema”

fail si fichier interdit

 Ajouter allowlist horodatée uniquement si indispensable (même format que issue 1.1)

 Ajouter commande CI make ci-contracts

DoD

CI échoue dès qu’un JSON Schema apparaît hors packages/contracts/schemas

Les templates OpenSearch/Qdrant ne déclenchent pas de faux positifs (via whitelist)

Risques & mitigation

Confusion schema vs template
→ whitelist par répertoires très précis + doc.

Issue 1.4 — Cartographie “modules à risque” (drift map) + baseline

Title: docs(architecture): add drift-risk map (baseline hotspots) + tracking
Labels: docs, architecture, drift
Priority: P1 (mais très utile)

Objectif

Rendre visible ce qui dérive et où agir en PHASE 2/3/4/5/6.

Scope exact

Produire un doc “hotspots” + une baseline mesurable :

routes trop lourdes

duplication search/persistence

packages qui importent des libs interdites (même si allowlist)

endroits où contracts ne sont pas utilisés

Format recommandé

docs/architecture/drift-map.md avec :

Tableau “Hotspot” / “Pourquoi risque” / “Symptômes” / “Plan de migration”

Liens vers fichiers/dossiers précis

Une section “exceptions temporaires” avec date d’expiration

Steps (checklist)

 Générer une liste initiale (manuelle au début) :

services/api/src/routes/search.py + services/api/src/search/**

services/workers/indexer/src/** (clients search)

services/workers/ingest/src/db/**, services/workers/transcribe/src/db/**

services/workers/enrich/src/layers/**

 Ajouter une section “metrics” simple :

nombre d’entrées allowlist

nombre de violations (si mode report)

coverage contract tests (nb de schemas couverts)

DoD

Un doc unique liste les hotspots + owner + phase cible

La réduction de drift devient traçable (allowlist count ↓, hotspots supprimés)

Risques & mitigation

Doc qui vieillit
→ mettre une règle : toute exception CI doit être référencée dans drift-map (avec expiry).

Définition de Done (PHASE 1)

✅ dependency boundaries check en CI (avec allowlist horodatée + expiry enforced)

✅ no schema duplication check en CI

✅ tests/contract étendus : au moins search + jobs + entities + layer envelope

✅ drift-map initial documenté (hotspots + plan)

✅ CI échoue sur violations (pas juste warnings)

Si tu veux, je peux aussi te proposer le contenu exact de dependency_boundaries.yaml (règles par dossier) et les noms d’imports à blacklister (psycopg/asyncpg/sqlalchemy/opensearch/qdrant/fastapi/etc.) adaptés à ta stack Python actuelle.
