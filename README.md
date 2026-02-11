# Narralytica

**Narralytica** is an infrastructure for **video speech intelligence**.

It transforms long-form spoken video content (YouTube, conferences, interviews, podcasts) into **structured, searchable, and analyzable knowledge**.

Narralytica is **not an end-user product**.  
It is the **core intelligence layer** powering multiple specialized applications.

---

## 🧠 What Narralytica Does

Narralytica turns raw video into:

- Time-coded speech segments  
- Speaker-aware transcripts  
- Semantic embeddings  
- AI enrichment layers (topics, summaries, tone, stance, CEFR…)  
- Hybrid search indexes (semantic + lexical)  
- APIs for querying, analysis, and reuse  

It is effectively:

> **A search engine + AI understanding layer for everything said in video.**

---

## 🧩 Platform Architecture

Narralytica is composed of four major layers:

### 1️⃣ Ingestion
Transforms raw video into structured data:
- Metadata extraction
- Audio extraction
- Transcription
- Timecoded segmentation
- Speaker diarization

### 2️⃣ AI Enrichment
Each segment can be enriched with:
- Embeddings (semantic meaning)
- Summaries
- Topic detection
- Sentiment / tone
- Position detection (for/against)
- CEFR language level
- Key moment scoring

### 3️⃣ Search Infrastructure
Supports:
- Semantic search (vector DB)
- Lexical search (OpenSearch)
- Hybrid retrieval and reranking
- Filtering by speaker, topic, language, time, source

### 4️⃣ API Layer
Provides programmatic access to:
- Segments
- Transcripts
- Speakers
- Topics
- Trends
- Search

---

## 🚀 What It Powers

Narralytica feeds multiple end-user products:

| Product | Purpose |
|--------|---------|
| VideoResearch Pro | Verifiable video citations for journalists & researchers |
| LinguaTube Studio | Language learning with real videos |
| InsightMonitor | Strategic monitoring of public discourse |
| Creator Intelligence | Content analysis for creators |
| SpeakerDNA | Analytical profiles of speakers |
| ClipQuote | Extract publishable video quotes |
| LectureFinder | Find the best explanations of a concept |
| DebateMap | Map arguments across video discourse |
| TrendPulse | Detect emerging ideas and trends |
| Idea Mining API | API access for external developers |

---

## 🛠 Tech Stack (V1)

- **Postgres** — source of truth
- **Object storage (S3/MinIO)** — media & artifacts
- **Qdrant** — vector search
- **OpenSearch** — lexical search
- **Python services** — API + workers
- **Docker Compose** — local development

---

## 🧪 Local Development

```bash
docker compose up
```

Then run services locally via the API and worker modules (see /docs/runbooks/local-dev.md).

## 📚 Documentation

All technical documentation lives under /docs:

Architecture: docs/architecture/

Runbooks: docs/runbooks/

Specs: docs/specs/

ADRs: docs/adr/

Delivery planning and execution order are defined in /epics.

## 🧭 Project Governance

Roadmap & execution order: epics/roadmap.md

EPIC structure: epics/README.md

Architecture decisions: docs/adr/

## ⚖️ License

See LICENSE.
