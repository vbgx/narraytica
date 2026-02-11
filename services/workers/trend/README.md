# Trend Worker — Narralytica

The Trend worker computes **aggregate insights over time** from enriched video segments.

It powers features related to:
- Emerging topics
- Shifts in discourse
- Speaker activity trends
- Sentiment evolution

This worker operates at the **analytical layer**, not the per-video processing layer.

---

## 🎯 Purpose

The trend worker is responsible for:

- Aggregating segment-level data across time
- Detecting increases or decreases in topic frequency
- Tracking how sentiment or stance evolves
- Building datasets for dashboards and analytics APIs

It transforms raw enriched data into **temporal intelligence**.

---

## 📥 Inputs

The worker consumes:

- Segments with timestamps
- Enrichment layers (topics, sentiment, stance, CEFR)
- Speaker information
- Time windows or aggregation parameters

Jobs may be:
- Scheduled (daily/weekly)
- Triggered after large backfills
- Triggered manually for recomputation

---

## 📤 Outputs

After processing, the worker produces:

| Artifact | Location | Description |
|---------|----------|-------------|
| Topic trend series | Database / analytics store | Topic frequency over time |
| Sentiment trends | Database | Sentiment distribution over time |
| Speaker activity metrics | Database | Speaker presence trends |
| Job status update | Database | Marks trend job completed |

These outputs support products like **TrendPulse Video** and monitoring dashboards.

---

## 🧱 Responsibilities

| Task | Description |
|------|-------------|
| Time bucketing | Group segments by day/week/month |
| Topic aggregation | Count topic occurrences over time |
| Sentiment aggregation | Track emotional tone trends |
| Stance aggregation | Track shifts in positions |
| Speaker metrics | Measure speaker visibility over time |

---

## ⚙️ Performance Considerations

- Aggregations may involve large datasets
- Queries must be optimized and possibly precomputed
- Incremental updates should be preferred over full recompute
- Historical backfills may require batch processing

---

## 🔄 Idempotency

If the same trend job runs multiple times:

- Aggregates should be recomputed or safely updated
- Duplicate trend records must not be created
- Results must remain consistent

---

## 🚫 Out of Scope

The trend worker does **not**:

- Process raw media
- Perform transcription or enrichment
- Serve API requests directly
- Index search data

It focuses only on **analytics over processed data**.

---

## 🛠 Runbook

Operational procedures for rerunning or debugging trend jobs are documented in:

`services/workers/trend/RUNBOOK.md`

---

## 📚 Related Documentation

- Data model → `docs/architecture/data-model.md`
- Pipelines → `docs/architecture/pipelines.md`
- Analytics consumers → `apps/trendpulse/`

