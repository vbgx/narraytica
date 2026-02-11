# Database — Narralytica

This package contains the **database layer definition** for Narralytica.

Postgres is the **source of truth** for all structured platform data.  
Everything else (search indexes, AI layers, caches) is derived from it.

---

## 🎯 Purpose

This package exists to:

- Define the relational schema
- Manage database migrations
- Provide seed data for development
- Document views and derived structures

It ensures the data model remains **versioned, consistent, and auditable**.

---

## 📦 What’s Inside

| Folder / File | Purpose |
|---------------|---------|
| `migrations/` | Ordered SQL migrations |
| `seeds/` | Development and test seed data |
| `views/` | Database views for read models |
| `schema.md` | Human-readable explanation of the schema |
| `README.md` | Usage and conventions (this file) |

---

## 🧱 Schema Philosophy

The database stores:

- Videos and metadata
- Transcripts
- Timecoded segments
- Speakers
- AI enrichment layer references
- Processing job state

The database **does not store**:
- Large binary artifacts (audio, embeddings)
- Search indexes
- Temporary pipeline state

Those belong in object storage or search infrastructure.

---

## 🔄 Migrations

Migrations are:

- Sequentially numbered (`0001_*.sql`)
- Immutable once applied
- The only way to change the schema

### Running Migrations

Handled via CI/CD or deployment scripts.  
Never modify schema directly in production.

---

## 🌱 Seeds

Seed data is used for:

- Local development
- Integration testing
- Demo datasets

Seeds must never include sensitive or production data.

---

## 🧠 Views

Views may be used to:

- Simplify read patterns
- Support analytics queries
- Prepare data for indexing or export

Views must not contain business logic that belongs in services.

---

## 🔐 Data Integrity

The database enforces:

- Referential integrity (foreign keys)
- Constraints where appropriate
- Consistent IDs across entities

Application code must respect these invariants.

---

## 📚 Related Documentation

- Data model explanation → `schema.md`
- Architecture overview → `docs/architecture/data-model.md`
- Pipelines → `docs/architecture/pipelines.md`
