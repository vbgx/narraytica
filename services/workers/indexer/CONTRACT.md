# Indexer Worker Contract — Narralytica

This document defines the **job payload and output artifacts** for the Indexer worker.

It is the formal contract between:
- The orchestrator (job producer)
- The indexer worker (job consumer)
- The search infrastructure (downstream systems)

---

## 📥 Job Input Contract

The indexer worker expects a job payload structured as follows:

```json
{
  "job_id": "string",
  "video_id": "string",
  "segments_ref": "string",
  "layers_ref": "string",
  "embeddings_ref": "string",
  "reindex": "boolean (optional)"
}
```

## Field Descriptions

| Field            | Description                             |
| ---------------- | --------------------------------------- |
| `job_id`         | Unique identifier for this indexing job |
| `video_id`       | Canonical video ID                      |
| `segments_ref`   | Reference to segmented transcript data  |
| `layers_ref`     | Reference to enrichment layer data      |
| `embeddings_ref` | Reference to embedding vectors          |
| `reindex`        | Optional flag to force full reindex     |


## 📤 Output Artifacts

After successful indexing, the worker must produce:

| Artifact          | System     | Description                           |
| ----------------- | ---------- | ------------------------------------- |
| Search documents  | OpenSearch | Lexical search index entries          |
| Vector points     | Qdrant     | Embedding vectors for semantic search |
| Job status update | Database   | Job marked as completed               |


Indexed documents must conform to:

`packages/contracts/schemas/search.schema.json`

---

## 🧱 Indexing Rules
Lexical Index (OpenSearch)

Each segment document must include:

Segment text

Video metadata (title, channel, date)

Speaker ID

Topics, sentiment, stance, CEFR

Language code

Timecodes

Vector Index (Qdrant)

Each segment vector must include:

Embedding vector

Segment ID

Video ID

Metadata for filtering (language, speaker, date)

---

## 🔄 State Transitions

| State       | Meaning                                    |
| ----------- | ------------------------------------------ |
| `pending`   | Job created but not started                |
| `running`   | Indexing in progress                       |
| `failed`    | Indexing failed in one or more systems     |
| `completed` | Both lexical and vector indexing succeeded |


---

## 🧱 Guarantees

The indexer worker guarantees:

Documents are upserted (not duplicated)

Vectors are stored before marking job complete

Reindexing safely replaces previous index entries

Lexical and vector indexes remain consistent

## 🚫 Non-Responsibilities

The indexer worker does not:

Generate embeddings

Perform AI enrichment

Modify transcript or speaker data

Serve search queries

It only prepares data for search systems.

## 📚 Related Contracts

Segment schema → `packages/contracts/schemas/segment.schema.json`

Layer schema → `packages/contracts/schemas/layer.schema.json`

Search schema → `packages/contracts/schemas/search.schema.json`
