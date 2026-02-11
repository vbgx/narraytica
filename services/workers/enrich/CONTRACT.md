# Enrich Worker Contract — Narralytica

This document defines the **job payload and output artifacts** for the Enrich worker.

It formalizes the contract between:
- The orchestrator (job producer)
- The enrich worker (job consumer)
- The indexer and analytics layers (downstream consumers)

---

## 📥 Job Input Contract

The enrich worker expects a job payload structured as follows:

```json
{
  "job_id": "string",
  "video_id": "string",
  "segments_ref": "string",
  "layers": [
    "embeddings",
    "summaries",
    "topics",
    "sentiment",
    "stance",
    "cefr"
  ],
  "model_config": {
    "embedding_model": "string (optional)",
    "llm_model": "string (optional)"
  }
}
```

## Field Descriptions

| Field          | Description                               |
| -------------- | ----------------------------------------- |
| `job_id`       | Unique identifier for this enrichment job |
| `video_id`     | Canonical video ID                        |
| `segments_ref` | Reference to segmented transcript data    |
| `layers`       | List of AI layers to compute              |
| `model_config` | Optional model overrides                  |


---

## 📤 Output Artifacts

| Artifact          | Location        | Description                                 |
| ----------------- | --------------- | ------------------------------------------- |
| Embedding vectors | Vector database | One vector per segment                      |
| Layer records     | Database        | Structured outputs for each requested layer |
| Job status update | Database        | Job marked as completed                     |


Layer outputs must follow the schema defined in:

`packages/contracts/schemas/layer.schema.json`

---

## 🧠 Layer Definitions

| Layer        | Output Type                               |
| ------------ | ----------------------------------------- |
| `embeddings` | Dense semantic vector                     |
| `summaries`  | Short natural-language summary            |
| `topics`     | One or more subject labels                |
| `sentiment`  | Positive / neutral / negative             |
| `stance`     | For / against / neutral (when applicable) |
| `cefr`       | Language difficulty level (A1–C2)         |


Each layer is independently versionable.

## 🔄 State Transitions

| State       | Meaning                                    |
| ----------- | ------------------------------------------ |
| `pending`   | Job created but not started                |
| `running`   | Enrichment in progress                     |
| `failed`    | At least one requested layer failed        |
| `completed` | All requested layers computed successfully |


---

## 🧱 Guarantees

The enrich worker guarantees:

Each segment receives at most one record per layer per version

Vectors are stored before marking job complete

Reprocessing replaces or versions previous layer outputs safely

Partial failures are recorded and visible

---

## 🚫 Non-Responsibilities

The enrich worker does not:

Fetch raw media or audio

Perform transcription or diarization

Handle search indexing

Serve data directly to users

Those concerns belong to other services.

---

📚 Related Contracts

- Segment schema → `packages/contracts/schemas/segment.schema.json`

- Layer schema → `packages/contracts/schemas/layer.schema.json`

- Search schema → `packages/contracts/schemas/search.schema.json`

---



