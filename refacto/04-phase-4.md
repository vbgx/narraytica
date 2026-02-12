# PHASE 4 — Persistence adapters (Postgres repos) — Milestone REFACTO

Objectif
Éviter que chaque route/worker réimplémente l’accès Postgres (SQL, transactions, mappers, erreurs).
À la fin : un seul point d’accès DB partagé, consommé par API + workers, avec sémantique verrouillée par tests.

Scope exact

Centraliser Postgres dans packages/persistence/postgres/*

Migrer progressivement les accès DB “locaux” depuis :

services/workers/ingest/src/db/*

services/workers/transcribe/src/db/*

(et tout accès DB direct dans l’API au-delà du wiring)

Repos à couvrir :

Jobs / JobRuns / JobEvents

Videos

Segments

Transcripts

Speakers

Principe

packages/persistence = adapters IO (DB) + mapping + transaction helpers

packages/domain = types/invariants (NO IO)

packages/application = use-cases (appelle des ports repos, pas SQL)

services/* = wiring + runtime

Issue 4.1 — Introduire packages/persistence/postgres (db/tx/errors) + conventions

Title: refactor(persistence): introduce packages/persistence/postgres foundation (db/tx/errors)
Labels: refactor, persistence, postgres, architecture
Priority: P0

Objectif

Créer la fondation technique Postgres partagée : connexions, transactions, erreurs normalisées.

Scope exact

Créer la structure :

packages/persistence/
  postgres/
    __init__.py
    db.py            # pool/conn factory
    tx.py            # transaction scope helpers
    errors.py        # exceptions DB normalisées
    README.md        # règles d'usage + patterns

Conventions à figer (anti-drift)

Les repos lèvent des erreurs “propres” :

NotFound, Conflict, PreconditionFailed, RetryableDbError

Les transactions sont explicites via tx.transaction(conn) (ou async context manager)

Aucun import FastAPI / HTTPException ici

Steps

 Créer db.py (connexion/pool aligné sur ta lib actuelle)

 Créer tx.py (context manager transaction : commit/rollback)

 Créer errors.py + mapping d’erreurs driver → erreurs normalisées

 Ajouter README.md (patterns : “repo methods return domain models” / “mappers only”)

 Ajouter test smoke : open/close conn, transaction rollback (sans logique métier)

DoD

Package importable, stable, tests smoke passent

Transactions et erreurs sont standardisées (une seule manière de faire)

Risques & mitigation

Mismatch sync/async entre API/workers
→ décider une stratégie et s’y tenir (ou wrappers explicites, mais pas deux impl “cachées”).

Issue 4.2 — Définir “ports” repos côté application + contrats de retour

Title: refactor(application): define persistence repo ports (jobs/videos/segments/transcripts/speakers)
Labels: application-layer, persistence, refactor
Priority: P0

Objectif

Le cerveau (use-cases) parle à la DB via interfaces, pas via impl Postgres.

Scope exact

Dans packages/application/ports/persistence_ports.py (ou équivalent) :

JobsRepoPort

VideosRepoPort

SegmentsRepoPort

TranscriptsRepoPort

SpeakersRepoPort

Steps

 Définir signatures minimales nécessaires aux flows existants (ingest/transcribe/search/jobs)

 Définir types de retour (domain models) + erreurs attendues

 Ajouter tests unitaires “port compliance” (au moins typing + mocks)

DoD

Use-cases peuvent être écrits/testés avec mocks de repos

Les impl Postgres devront juste “matcher” ces ports

Risques & mitigation

Ports trop grands
→ v0 minimal : seulement ce qui est utilisé actuellement.

Issue 4.3 — Implémenter JobsRepo (Job/JobRun/JobEvent) + mappers (v0)

Title: refactor(persistence): implement JobsRepo (jobs/job_runs/job_events) in shared postgres repos
Labels: persistence, jobs, postgres, refactor
Priority: P0 (c’est le pivot runtime)

Objectif

Centraliser la sémantique la plus sensible : statuts, transitions, idempotence, events.

Structure cible
packages/persistence/postgres/
  mappers/
    jobs.py
  repos/
    jobs_repo.py

Scope exact (fonctionnel)

CRUD job

création job_run (avec attempt, timestamps)

append job_event (enveloppe conforme contracts)

queries : get job status, list runs, list events

Steps

 Écrire mappers/jobs.py (row → domain model)

 Écrire repos/jobs_repo.py (SQL + tx)

 Ajouter tests unitaires (mappers) + tests d’intégration (repo) :

create job

create run

append event

read back

 Ajouter test idempotence (si applicable) :

même request key → pas de duplication (ou comportement explicitement défini)

DoD

JobsRepo remplace la logique DB jobs dispersée

Tests passent + transaction rollback test

Risques & mitigation

Différences de semantics (ex: event ordering)
→ fixer ordering (occurred_at, seq) + tests.

Issue 4.4 — Implémenter repos “content” (Videos/Segments/Transcripts/Speakers) + mappers

Title: refactor(persistence): implement shared repos for videos/segments/transcripts/speakers (with mappers)
Labels: persistence, postgres, refactor
Priority: P1 (après JobsRepo)

Objectif

Retirer la duplication DB des workers ingest/transcribe.

Structure cible
packages/persistence/postgres/
  mappers/
    videos.py
    segments.py
    transcripts.py
    speakers.py
  repos/
    videos_repo.py
    segments_repo.py
    transcripts_repo.py
    speakers_repo.py

Scope exact (fonctionnel minimal)

Videos: upsert + get

Segments: bulk insert/upsert + get by video/transcript

Transcripts: create/update + get

Speakers: upsert + link segments (si modèle le requiert)

Steps

 Implémenter mappers + repos

 Ajouter tests d’intégration “round trip” :

persist transcript + segments

read back same shape

 Ajouter contraintes attendues (unique keys) via migrations si nécessaires (sinon tests vont révéler le drift)

DoD

Workers peuvent s’appuyer sur ces repos sans SQL local

Tests d’intégration passent

Risques & mitigation

Bulk perf (segments)
→ prévoir method bulk_upsert_segments() avec batching + tests “does not explode”.

Issue 4.5 — Migrer workers/ingest : remplacer src/db/* par repos partagés (compat layer)

Title: refactor(workers): migrate ingest worker DB access to shared repos (remove local db/*)
Labels: workers, persistence, refactor
Priority: P0

Objectif

Le worker ingest ne doit plus contenir de SQL/clients Postgres propres.

Stratégie de migration (progressive)

Créer une façade locale temporaire :

services/workers/ingest/src/db_facade.py

Cette façade appelle packages/persistence/postgres/repos/*

Puis suppression de services/workers/ingest/src/db/*

Steps

 Inventorier fonctions DB actuellement utilisées dans ingest

 Ajouter méthodes manquantes aux repos partagés

 Implémenter db_facade.py (mêmes signatures que l’ancien module db)

 Remplacer imports dans worker vers db_facade.py

 Supprimer progressivement src/db/*

 Mettre à jour boundaries CI : interdire imports DB driver dans workers/ingest (sauf via packages)

DoD

workers/ingest n’a plus de répertoire src/db/* “métier”

CI boundaries passe sans allowlist pour ingest

Tests ingest (integration) passent inchangés

Risques & mitigation

Transactions implicites (avant/after)
→ ajouter tests “happy path + rollback” sur ingestion.

Issue 4.6 — Migrer workers/transcribe : remplacer src/db/* par repos partagés

Title: refactor(workers): migrate transcribe worker DB access to shared repos (remove local db/*)
Labels: workers, persistence, refactor
Priority: P0

Objectif

Même outcome que ingest : plus de DB locale.

Steps

 Inventory transcribe DB usage (transcripts/segments/speakers/job events)

 Compléter repos si manque

 Implémenter façade services/workers/transcribe/src/db_facade.py

 Remplacer imports

 Supprimer src/db/* legacy

 Ajouter boundary CI “no DB driver import in transcribe worker”

DoD

DB logic transcribe centralisée

Tests transcribe passent + rollback test

Risques & mitigation

Modèle speakers/segments complexe
→ isoler méthode repo “link speaker to segments” avec tests.

Issue 4.7 — API: déplacer accès DB hors routes vers wiring + repos (si résidus)

Title: refactor(api): ensure api routes do not access Postgres directly (repos via wiring only)
Labels: api, persistence, refactor
Priority: P1 (selon état réel)

Objectif

Conformer l’API au principe “routes = glue”.

Steps

 Identifier accès DB direct dans services/api/src/routes/**

 Injecter repos via services/api/src/wiring/persistence.py

 Remplacer SQL/driver calls par appels use-cases + repos ports

DoD

Routes n’importent plus de driver/ORM Postgres

CI boundaries “routes no IO” passe

Risques & mitigation

Refacto en cascade
→ limiter à /jobs, /ingest prioritaire.

Issue 4.8 — Tests “DB semantics freeze” (anti-drift Postgres)

Title: tests(persistence): add DB semantics tests (constraints, invariants, tx boundaries)
Labels: tests, persistence, drift
Priority: P0 (verrou qualité)

Objectif

Geler ce qui doit être vrai côté DB : contraintes, ordering, idempotence, invariants transactionnels.

Couverture minimale

JobsRepo :

create job / run

append event ordering stable

not found / conflict

Transcripts + Segments :

persist + read back shape

unique constraints (ex: segment_id unique per transcript)

Transactions :

un failure au milieu → rollback (pas de demi-écritures)

Steps

 Tests d’intégration Postgres (docker compose/CI service)

 Ajouter fixtures (1 transcript, 3 segments, 2 speakers)

 Ajouter tests rollback

 Ajouter test “migration drift” si tu as une commande standard pour appliquer migrations

DoD

CI casse si les invariants DB changent

Les repos partagés ont une couverture d’intégration minimale

Risques & mitigation

CI plus lente
→ garder set minimal, batch tests, pas de gros volumes.

Issue 4.9 — CI strict: interdire imports DB drivers hors packages/persistence (sans allowlist)

Title: ci(architecture): forbid Postgres driver imports outside packages/persistence (strict)
Labels: ci, architecture, drift
Priority: P0 (clôture de phase)

Objectif

Empêcher tout retour en arrière.

Steps

 Dans dependency boundaries checker :

denylist psycopg|asyncpg|sqlalchemy hors packages/persistence/postgres/**

 Supprimer allowlist liée à DB (ou la faire tomber à 0)

 Ajouter un test “no local db modules” pour workers ingest/transcribe

DoD

CI échoue sur tout import DB driver hors persistence

Aucune exception restante pour DB

Risques & mitigation

Un worker “oublié” (autre que ingest/transcribe) utilise Postgres direct
→ le check le révèle immédiatement : migration rapide ou ajout repo method.

Définition de Done (PHASE 4)

✅ packages/persistence/postgres est la source unique de Postgres access

✅ workers/ingest et workers/transcribe n’ont plus de src/db/* métier

✅ API routes n’importent plus de driver/ORM

✅ Tests d’intégration DB + rollback protègent les invariants

✅ CI interdit les imports DB drivers hors packages/persistence (strict, sans allowlist)
