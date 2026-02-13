# PHASE 2 — Extraction Use-cases (Application layer) depuis API — Milestone REFACTO

Objectif
Sortir l’orchestration et la logique métier des routes FastAPI, sans changer le comportement, en introduisant packages/application/* (use-cases) + en migrant services/api/src/domain/* vers packages/domain (invariants) et packages/application (orchestration).

Scope prioritaire
/ingest, /jobs, /search (car ce sont les surfaces de drift les plus coûteuses).

Principe de phase
On ne refait pas les features : on déplace la logique vers un endroit stable, en gardant des wrappers compat dans l’API au début.

## Issue 2.1 — Créer packages/application (squelette + règles + “ports”)

Title: refactor(application): introduce packages/application skeleton (ports + use_cases)
Labels: refactor, architecture, application-layer
Priority: P0

Objectif

Créer l’espace canonique d’orchestration (use-cases) et fixer les règles anti-drift :

pas de HTTP

pas d’IO direct (DB/search/LLM) en dur

tout IO passe via ports (interfaces) injectées depuis services (API/workers)

Scope exact

Créer une structure minimale :

packages/application/
  README.md
  ports/
    __init__.py
    persistence_ports.py
    search_ports.py
    media_ports.py          # ffprobe/storage/transcribe/etc (si nécessaire)
    ai_ports.py             # plus tard (phase 5)
    observability_ports.py
  use_cases/
    __init__.py
    ingest.py
    jobs.py
    search.py
  errors.py                 # erreurs applicatives (pas HTTP)

Steps (checklist)

 Créer packages/application/README.md avec règles :

“no fastapi imports”

“no DB/search clients”

“use ports only”

 Créer ports/* (interfaces Python / Protocols)

 Créer errors.py (ApplicationError, NotFound, ValidationError, Conflict, Retryable)

 Créer use_cases/ingest.py, jobs.py, search.py avec signatures v0 (stubs)

 Ajouter tests smoke “importability” (tests/unit/test_application_imports.py)

 Ajouter règle de boundaries (PHASE 1) : packages/application ne peut pas importer FastAPI/clients infra

DoD

packages/application est importable en CI

Les ports sont définis (même si encore non utilisés partout)

Les use-cases existent (stubs) et exposent une API stable pour que routes puissent déléguer

Risques & mitigation

Surdesign ports : trop d’interfaces, peu utilisées
→ v0 minimal : seulement ce qui est nécessaire à /search, /jobs, /ingest.

## Issue 2.2 — Définir des DTO/Contracts boundary (API ↔ use-cases) sans fuite FastAPI

Title: refactor(application): define boundary DTOs for ingest/jobs/search (contract-first)
Labels: refactor, contracts, application-layer
Priority: P0

Objectif

Faire en sorte que les routes n’échangent pas des objets FastAPI/Pydantic “ad-hoc” avec le cerveau.
La frontière doit être :

types contracts (JSON schema) ou DTO internes alignés sur contracts

erreurs applicatives (pas HTTPException)

Scope exact

Définir 3 ensembles de types boundary :

SearchQueryDTO, SearchResultDTO

CreateJobDTO, JobStatusDTO, JobEventDTO

IngestRequestDTO, IngestResultDTO

Steps

 Créer packages/application/use_cases/_dtos.py (ou 1 fichier par domaine)

 Ajouter “schema validation” optionnelle à l’entrée des use-cases (via helper qui valide contre packages/contracts)

 Ajouter golden fixtures des DTOs dans tests/fixtures/contracts/* si pas déjà

DoD

Routes peuvent appeler use-case en passant un dict/DTO validable, sans importer services/api internals

Les tests contract couvrent request/response pour search/jobs/ingest (au moins minimal)

Risques & mitigation

Double modélisation (DTO + schema)
→ DTO = “shape Python”, schema = “source of truth”. DTO doit rester thin.

## Issue 2.3 — Extraction SEARCH: routes → use_case.search (sans changer output)

Title: refactor(search): move search orchestration out of routes into application use-case
Labels: refactor, search, application-layer
Priority: P0

Objectif

services/api/src/routes/search.py devient glue :

validate input

call packages/application/use_cases/search.py

map result

return

Scope exact (ce qui sort des routes)

normalisation/validation des filtres (si aujourd’hui dans services/api/src/domain/search_filters.py)

sélection lexical/vector/hybrid + merge/ranking orchestration (même si impl encore en services/api/src/search/* à ce stade)

mapping d’erreurs (ex: “bad query”) vers erreurs applicatives

Steps

 Implémenter SearchUseCase.execute(query_dto, deps) dans packages/application/use_cases/search.py

 Définir ports nécessaires :

SearchEnginePort (temporaire) ou LexicalSearchPort/VectorSearchPort (si déjà)

ObsPort pour search.executed

 Dans routes/search.py :

remplacer logique par appel use-case

garder exactement les mêmes réponses (contract + tests)

 Ajouter golden tests “filters semantics” (exemples stables)

 Ajouter golden test “hybrid merge” si existant partiellement : le rendre explicite

DoD

routes/search.py ne contient plus de logique “deep” (enforced par boundaries)

Les tests d’intégration existants (ex: test_search_e2e) passent inchangés

Les nouveaux golden tests protègent la sémantique

Risques & mitigation

Régression sémantique invisible
→ golden tests + fixtures réalistes.

Issue 2.4 — Extraction JOBS: routes → use_case.jobs + normalisation events

Title: refactor(jobs): move jobs orchestration into application use-case (no behavior change)
Labels: refactor, jobs, application-layer
Priority: P0

Objectif

Routes jobs = glue.
La création/lecture/mise à jour statut + emission job events = use-case.

Scope exact

Sortir des routes :

logique “status transitions”

formatage d’events job_event

règles d’idempotence de création (si présentes)

Garder mêmes endpoints, mêmes codes de statut, mêmes payloads

Steps

 Implémenter JobsUseCase :

create_job()

get_job(job_id)

list_jobs(filters)

append_job_event(job_id, event)

 Définir ports :

JobsRepoPort (lecture/écriture)

ObsPort (emit job.*)

 Adapter routes/jobs.py pour déléguer

 Ajouter contract tests : job, job_run, job_event

DoD

Aucune logique de transition/statut dans routes/jobs.py

Les events jobs émis sont conformes schema job_event.schema.json

Tests integration jobs passent

Risques & mitigation

Couplage DB (si routes parlent SQL directement)
→ le port JobsRepoPort peut d’abord déléguer à l’existant, PHASE 4 unifie les repos.

Issue 2.5 — Extraction INGEST: routes → use_case.ingest (API ne fait plus que déclencher)

Title: refactor(ingest): move ingest orchestration into application use-case (trigger only in API)
Labels: refactor, ingest, application-layer
Priority: P1 (car dépend parfois de ton architecture jobs/workers)

Objectif

L’API /ingest ne fait pas “ingestion”. Elle déclenche un job/run, valide l’input, et retourne.

Scope exact

Sortir :

préparation des inputs job (storage refs, video metadata refs)

création job + job_run

emission events ingest.requested / job.created

Steps

 Implémenter IngestUseCase.request_ingest(input_dto, deps)

 Ports :

JobsRepoPort

MediaRefPort (si besoin de valider un storage ref)

ObsPort

 Adapter routes/ingest.py

 Ajouter tests contract request/response ingest (minimal)

DoD

Route ingest = glue, aucune logique deep

Ingest déclenche un job de façon idempotente (si applicable) ou au moins documentée

Risques & mitigation

Ambiguïté “API vs worker”
→ règle simple : API “requests”, worker “executes”.

Issue 2.6 — Supprimer (ou réduire à wrappers) services/api/src/domain/* (anti-domain-in-api)

Title: refactor(api): deprecate services/api/src/domain/* (move to packages/domain + application)
Labels: refactor, architecture, drift
Priority: P0

Objectif

Éliminer la “deuxième vérité” : domain logic ne doit plus vivre dans l’API.

Scope exact

Cibles typiques :

search_filters.py

ingestion_contract.py

ingestion_validation.py

tout “business rules” dans services/api/src/domain/*

Stratégie migration (compat)

Laisser des wrappers transitoires :

services/api/src/domain/search_filters.py → délègue à packages/...

Allowlist horodatée (PHASE 1) si nécessaire

Suppression complète en PHASE 7

Steps

 Déplacer invariants vers packages/domain/*

 Déplacer orchestration vers packages/application/*

 Remplacer imports dans routes

 Mettre wrappers legacy en “deprecated” + ajouter expiry allowlist

 Ajouter un check CI : “no new files in services/api/src/domain”

DoD

services/api/src/domain/* ne contient plus de logique (wrappers seulement au pire)

Aucune route n’importe services/api/src/domain/* pour faire du métier

Risques & mitigation

Oubli de cas edge
→ golden tests + integration existants inchangés.

Issue 2.7 — Golden tests: sémantique des filtres + hybrid merge (anti-régression)

Title: tests(search): add golden tests for filters semantics and hybrid merge
Labels: tests, search, drift
Priority: P0 (c’est ce qui protège la phase)

Objectif

Prévenir les régressions qui “passent” mais changent le sens du produit.

Scope exact

Tests unitaires stables sur :

normalisation filtres (ranges, languages, speaker filters, time windows)

merge hybrid (tie-breaking, scoring, dedup)

Tests “golden” = snapshots JSON de SearchQueryNormalized et SearchResultMerged

Steps

 Créer fixtures input tests/fixtures/search/queries/*.json

 Ajouter tests :

tests/unit/test_search_filters_golden.py

tests/unit/test_hybrid_merge_golden.py

 Ajouter 1 cas multilingue + 1 cas “speaker filter + time window”

 S’assurer que tests ne dépendent pas d’OpenSearch/Qdrant (pure functions)

DoD

Les sorties golden sont stables et versionnées

Toute modification de sémantique force une décision explicite (update snapshot + rationale)

Risques & mitigation

Snapshots fragiles
→ snapshot uniquement des champs sémantiques, pas de timestamps/ids aléatoires.

Définition de Done (PHASE 2)

✅ packages/application existe (ports + use-cases + erreurs), sans imports HTTP/infra

✅ /search, /jobs, /ingest routes sont devenues glue (enforced via CI boundaries)

✅ services/api/src/domain/* réduit à wrappers (ou fortement diminué), plus de logique métier dedans

✅ tests d’intégration existants passent inchangés

✅ golden tests protègent la sémantique search (filtres + merge)

Si tu veux, je peux aussi te donner une checklist de review “route glue” (5 items) et une suggestion de max LOC par route qui reste réaliste (ex: 80–120 hors imports/typing).
