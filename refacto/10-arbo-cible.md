narralytica/
├─ packages/
│  ├─ contracts/                         # ✅ Source of truth (JSON Schemas)
│  │  ├─ schemas/
│  │  │  ├─ api/
│  │  │  ├─ domain/
│  │  │  ├─ search/
│  │  │  ├─ jobs/
│  │  │  ├─ layers/
│  │  │  └─ observability/
│  │  └─ README.md
│  │
│  ├─ domain/                            # ✅ Types + invariants (NO IO)
│  │  ├─ models/
│  │  │  ├─ video.py
│  │  │  ├─ segment.py
│  │  │  ├─ speaker.py
│  │  │  ├─ transcript.py
│  │  │  └─ job.py
│  │  ├─ errors.py
│  │  ├─ ids.py
│  │  └─ README.md
│  │
│  ├─ application/                       # ✅ Use-cases (orchestration, NO HTTP)
│  │  ├─ ports/                          # Interfaces (IO behind ports)
│  │  │  ├─ persistence_ports.py
│  │  │  ├─ search_ports.py
│  │  │  ├─ media_ports.py
│  │  │  ├─ ai_ports.py
│  │  │  └─ observability_ports.py
│  │  ├─ use_cases/
│  │  │  ├─ ingest.py
│  │  │  ├─ jobs.py
│  │  │  ├─ search.py
│  │  │  └─ enrich.py
│  │  └─ README.md
│  │
│  ├─ ingestion/                         # 🧠 Couche 1 (déterministe, NO IO)
│  │  ├─ models.py
│  │  ├─ pipeline.py
│  │  ├─ normalizers.py
│  │  ├─ validators.py                   # validate vs contracts
│  │  └─ README.md
│  │
│  ├─ ai_layers/                         # 🧠 Couche 2 (pure, pluginable)
│  │  ├─ base.py                         # LayerComputer
│  │  ├─ registry.py
│  │  ├─ types.py
│  │  ├─ common/
│  │  │  ├─ hashing.py
│  │  │  └─ text_normalize.py
│  │  ├─ layers/
│  │  │  ├─ embeddings.py
│  │  │  ├─ topics.py
│  │  │  ├─ sentiment.py
│  │  │  ├─ stance.py
│  │  │  ├─ cefr.py
│  │  │  ├─ summaries.py
│  │  │  └─ key_moments.py
│  │  └─ README.md
│  │
│  ├─ search/                            # 🧠 Couche 3 (moteur unifié)
│  │  ├─ engine.py                       # SearchEngine.search(q)->r
│  │  ├─ filters.py
│  │  ├─ ranking.py
│  │  ├─ ports.py                        # Lexical/Vector/Hybrid ports
│  │  ├─ adapters/                       # IO impls (OpenSearch/Qdrant)
│  │  │  ├─ opensearch.py
│  │  │  └─ qdrant.py
│  │  └─ README.md
│  │
│  ├─ persistence/                       # Adapters DB (Postgres)
│  │  ├─ postgres/
│  │  │  ├─ db.py
│  │  │  ├─ tx.py
│  │  │  ├─ errors.py
│  │  │  ├─ mappers/
│  │  │  │  ├─ jobs.py
│  │  │  │  ├─ videos.py
│  │  │  │  ├─ segments.py
│  │  │  │  ├─ transcripts.py
│  │  │  │  └─ speakers.py
│  │  │  └─ repos/
│  │  │     ├─ jobs_repo.py
│  │  │     ├─ videos_repo.py
│  │  │     ├─ segments_repo.py
│  │  │     ├─ transcripts_repo.py
│  │  │     └─ speakers_repo.py
│  │  └─ README.md
│  │
│  ├─ observability/                     # Facade unique emit + context
│  │  ├─ context.py
│  │  ├─ emit.py
│  │  ├─ events.py
│  │  ├─ sinks/
│  │  │  ├─ logging_sink.py
│  │  │  └─ otel_sink.py                 # optionnel
│  │  └─ README.md
│  │
│  └─ adapters/                          # (optionnel) IO “non-DB/non-search”
│     ├─ ai_providers/                   # LLM/embeddings providers (ports impl)
│     └─ media/                          # ffprobe, storage, audio extract, etc.
│
├─ services/
│  ├─ api/
│  │  ├─ src/
│  │  │  ├─ main.py                      # composition root
│  │  │  ├─ routes/
│  │  │  │  ├─ search.py
│  │  │  │  ├─ jobs.py
│  │  │  │  ├─ videos.py
│  │  │  │  └─ ingest.py
│  │  │  ├─ wiring/                      # injection/adapters assembly
│  │  │  │  ├─ persistence.py
│  │  │  │  ├─ search.py
│  │  │  │  ├─ observability.py
│  │  │  │  └─ ai.py
│  │  │  └─ middleware/
│  │  │     └─ request_context.py        # request_id, ObsContext
│  │  └─ tests/
│  │     └─ integration/
│  │        └─ test_search_e2e.py
│  │
│  └─ workers/
│     ├─ ingest/
│     │  ├─ src/
│     │  │  ├─ worker.py                 # runtime only
│     │  │  └─ wiring.py
│     │  └─ tests/
│     ├─ transcribe/
│     │  ├─ src/
│     │  │  ├─ worker.py
│     │  │  └─ wiring.py
│     │  └─ tests/
│     ├─ diarize/
│     │  ├─ src/
│     │  │  ├─ worker.py
│     │  │  └─ wiring.py
│     │  └─ tests/
│     ├─ enrich/
│     │  ├─ src/
│     │  │  ├─ worker.py                 # appelle registry ai_layers
│     │  │  └─ wiring.py                 # ports + providers + persistence
│     │  └─ tests/
│     └─ indexer/
│        ├─ src/
│        │  ├─ worker.py                 # index sync, no local clients
│        │  └─ wiring.py
│        └─ tests/
│
├─ tests/
│  ├─ contract/                          # ✅ Contract tests (schemas-first)
│  │  ├─ _helpers.py
│  │  ├─ test_layer_schema.py
│  │  ├─ test_search_schema.py
│  │  ├─ test_job_event_schema.py
│  │  └─ ...
│  ├─ integration/
│  └─ load/
│
├─ infra/
│  ├─ docker/
│  ├─ migrations/                         # DB migrations (si centralisé ici)
│  ├─ opensearch/                         # templates/mappings/settings
│  └─ qdrant/
│
├─ tools/
│  ├─ ci/
│  │  ├─ check_dependency_boundaries.py
│  │  ├─ check_no_schema_duplication.py
│  │  ├─ dependency_boundaries.yaml
│  │  └─ README.md
│  └─ fixtures/
│
└─ docs/
   ├─ adr/
   ├─ specs/
   ├─ runbooks/
   └─ architecture/
      └─ rules.md                         # matrice + règles anti-drift
