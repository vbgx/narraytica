# PHASE 7 — Decommission & cleanup (verrou final anti-drift) — Milestone REFACTO

Objectif
Supprimer tout le legacy déplacé pendant les phases 2–6, retirer les compat layers temporaires, ramener les allowlists à zéro, et verrouiller la cible via CI.
À la fin : une seule vérité par responsabilité (contracts, search, persistence, ai_layers, observability) et impossible de réintroduire le drift sans casser CI.

Scope exact

Suppression des anciens modules désormais dupliqués

Suppression des allowlists temporaires (dependency boundaries, schema duplication, exceptions)

Suppression des wrappers de compat (façades transitoires)

Nettoyage imports / namespaces

Verrouillage CI “strict mode”

Alignement docs (architecture rules + runbooks)

Principe
PHASE 7 = phase “garbage collection” + “locking”.
Si tu gardes du legacy “au cas où”, tu recrées du drift.

Issue 7.1 — Zéro allowlist : supprimer toutes les exceptions temporaires (strict mode)

Title: ci(architecture): remove all temporary allowlists (strict mode)
Labels: ci, architecture, drift, refactor
Priority: P0

Objectif

Aucune exception active sur les règles d’imports et de duplication de schémas.

Scope exact

tools/ci/dependency_boundaries_allowlist.yaml

allowlist “no schema duplication” (si séparée)

exceptions temporaires “routes too fat” / imports legacy / modules transitoires

Steps (checklist)

 Exporter la liste des entrées allowlist restantes (compter + grouper par dossier)

 Pour chaque entrée :

 migrer le code vers le bon package ou

 supprimer le fichier legacy ou

 corriger la règle si réellement incorrecte (rare)

 Supprimer le fichier allowlist (ou le rendre vide)

 Ajouter une règle CI : si allowlist non vide ⇒ CI FAIL

 Ajouter une règle CI : si allowlist file existe ⇒ warning/then fail (optionnel)

DoD

0 entrée allowlist

CI casse si quelqu’un en réintroduit une

Risques & mitigation

Une exception “justifiée” apparaît
→ ça veut dire qu’une migration n’est pas terminée : retourner à la phase concernée.

Issue 7.2 — Decommission API legacy (search & domain): supprimer impl métier interne

Title: refactor(api): delete legacy search/domain modules (packages/* is single source)
Labels: api, search, domain, refactor
Priority: P0

Objectif

Éliminer la duplication “métier” côté API, source principale de drift.

Scope exact (typique)

Supprimer définitivement :

services/api/src/search/** (impl métier)

services/api/src/domain/** (si encore présent)

tous wrappers legacy qui ne font que déléguer vers packages/*

Steps

 Vérifier que routes/search.py appelle uniquement packages/application ou packages/search via wiring

 Supprimer services/api/src/search/**

 Supprimer services/api/src/domain/** (ou le vider puis delete)

 Mettre à jour imports + tests

 Mettre à jour dependency boundaries pour interdire la recréation de ces répertoires

DoD

Il n’existe plus de “moteur search” dans services/api

services/api est glue + wiring uniquement

CI boundaries prouve que routes n’importent pas infra clients

Risques & mitigation

Tests qui importaient du code legacy
→ refactor tests vers packages canonique (pas vers API internals).

Issue 7.3 — Decommission workers legacy : supprimer DB/search clients locaux & vieux helpers

Title: refactor(workers): delete local db/search client code (shared adapters only)
Labels: workers, persistence, search, refactor
Priority: P0

Objectif

Les workers ne doivent plus posséder leurs propres impl DB/search/LLM providers.

Scope exact

Supprimer :

services/workers/ingest/src/db/** (si un reste)

services/workers/transcribe/src/db/**

services/workers/indexer/src/opensearch/** / qdrant/**

services/workers/enrich/src/layers/** (legacy)

Steps

 Confirmer que workers importent :

Postgres repos depuis packages/persistence/postgres

adapters search depuis packages/search/adapters

layers via packages/ai_layers/registry

observability via packages/observability

 Supprimer répertoires legacy

 Mettre à jour wiring worker si nécessaire

 Ajouter check CI “no legacy dirs exist” (voir issue 7.7)

DoD

0 client DB/search/AI provider local dans workers

Workers = runtime + wiring + orchestration technique

Risques & mitigation

Diff config par worker (timeouts, pool size)
→ config via injection/wiring, pas via duplication de code.

Issue 7.4 — Supprimer compat layers (wrappers transitoires) & stabiliser la surface publique

Title: refactor(core): remove compatibility wrappers and old import paths (single canonical APIs)
Labels: refactor, architecture, cleanup
Priority: P0

Objectif

Empêcher la cohabitation “nouveau + ancien”, qui réintroduit du drift.

Scope exact

Supprimer tous modules qui ne font que :

importer un nouveau module

redéfinir une fonction/classe et déléguer

maintenir des signatures historiques

Exemples typiques :

services/api/src/domain/search_filters.py wrapper

services/api/src/search/search_engine.py wrapper

workers/*/db_facade.py si plus nécessaire

Steps

 Identifier wrappers par pattern (fichier < 50 lignes, délégation)

 Remplacer imports dans tout le repo vers les chemins canoniques (packages/*)

 Supprimer wrappers

 Ajouter “import sanity test” (voir issue 7.7) interdisant anciens chemins

DoD

Aucun ancien chemin d’import ne fonctionne encore

Tout le repo pointe vers les packages canoniques

Risques & mitigation

Dépendances cachées (scripts/outillage)
→ scan global + tests import sanity.

Issue 7.5 — Verrouillage CI strict : règles finales anti-drift (non contournables)

Title: ci(architecture): enforce strict rules (no IO in routes, no HTTP in packages, single-source search/persistence/obs)
Labels: ci, architecture, drift
Priority: P0

Objectif

Rendre la cible durable : toute régression casse immédiatement CI.

Règles finales (bloquantes)

R1 — No HTTP in packages

packages/** interdit d’importer fastapi/starlette/HTTPException

R2 — No IO clients in routes

services/api/src/routes/** interdit d’importer :

Postgres driver/ORM

OpenSearch/Qdrant clients

SDK providers IA

R3 — No duplicate clients in workers

services/workers/**/src/** interdit d’importer DB/search clients (hors packages adapters)

R4 — No schema duplication

JSON Schema uniquement dans packages/contracts/schemas/**

R5 — No local telemetry

instrumentation uniquement via packages/observability

Steps

 Activer strict mode sur les scripts PHASE 1

 Supprimer tous “warnings-only”

 Ajouter un job CI dédié “architecture-guardrails” (rapide)

DoD

CI strict passe sur main

Toute violation est détectée en PR

Risques & mitigation

Trop strict pour les tests
→ autoriser quelques imports dans tests/** via règles spécifiques (mais pas d’IO métier).

Issue 7.6 — Nettoyage repo : supprimer dossiers vides, renommer, standardiser conventions

Title: chore(repo): cleanup folders, normalize naming, remove dead code paths
Labels: cleanup, chore
Priority: P1

Objectif

Réduire la surface cognitive et éliminer les “pièges” (anciens dossiers qui restent).

Scope exact

Supprimer dossiers devenus vides

Harmoniser noms de modules (ex: ai_layers vs ai_layer)

Déplacer “templates” backend dans un emplacement unique (ex: infra/opensearch/templates ou packages/search/adapters/templates)

Steps

 Linter imports / format

 Détecter dead code (modules non importés)

 Nettoyer README/links

DoD

Tree reflète la cible, sans reliquats

Risques & mitigation

Suppression de code utilisé indirectement
→ tests + import sanity + smoke.

Issue 7.7 — Import sanity tests : interdire les chemins legacy (anti-régression)

Title: tests(architecture): add import sanity tests for legacy paths + forbidden dirs
Labels: tests, architecture, drift
Priority: P0

Objectif

Empêcher qu’un vieux chemin réapparaisse silencieusement (ou qu’un dossier legacy soit recréé).

Scope exact

Tests qui échouent si :

un fichier contient from services.api.src.search ou services.workers.*.db

un dossier legacy existe (ex: services/api/src/search/)

un import interdit est présent dans un dossier interdit

Steps

 Ajouter tests/architecture/test_no_legacy_paths.py (scan ripgrep/AST)

 Ajouter test “legacy dirs must not exist”

 Ajouter test “forbidden imports” (déjà CI, mais double sécurité côté tests)

DoD

Les tests cassent si un dev recrée un dossier legacy

Les tests cassent si un import legacy est introduit

Risques & mitigation

Faux positifs (docs qui mentionnent un path)
→ scope scan code only (.py), exclure docs/.

Issue 7.8 — Docs & runbooks : aligner documentation avec architecture réelle

Title: docs(architecture): update architecture rules + runbooks to match final structure
Labels: docs, architecture
Priority: P1

Objectif

Réduire le drift humain : la doc doit refléter l’architecture, sinon elle re-dérive.

Scope exact

docs/architecture/rules.md :

matrice dépendances

exemples “où mettre quoi”

process pour ajouter :

un nouveau filter search

un nouveau layer IA

un nouveau repo DB

docs/specs/events.md :

events names + payloads + correlation

services/workers/README.md :

workers = runtime, pas logique

packages/*/README.md :

responsabilités + règles d’import

Steps

 Mettre à jour docs

 Vérifier links via ton link-checker

 Ajouter une section “Common anti-patterns (drift)” (5 bullets)

DoD

Un dev peut onboard et faire une feature sans recréer du legacy

Docs passent markdownlint/link-checker

Définition de Done (PHASE 7)

✅ 0 allowlist / 0 exception temporaire

✅ Dossiers legacy supprimés (API search/domain internes, workers db/search locaux, layers legacy)

✅ Plus de wrappers de compat

✅ CI strict mode activé (architecture guardrails)

✅ Import sanity tests empêchent toute réintroduction

✅ Docs alignées avec l’architecture finale
