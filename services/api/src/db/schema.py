from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    Text,
    func,
)

# Alembic will use this metadata as the schema source of truth
metadata = MetaData()

# Minimal base schema (v0) — enough to initialize DB from scratch
videos = Table(
    "videos",
    metadata,
    Column("id", String, primary_key=True),
    Column("source", String, nullable=False),  # e.g. youtube/upload
    Column(
        "source_ref", String, nullable=False
    ),  # e.g. youtube video id, object key, etc.
    Column("title", Text, nullable=True),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
)

jobs = Table(
    "jobs",
    metadata,
    Column("id", String, primary_key=True),
    Column("video_id", String, nullable=False),
    Column("type", String, nullable=False),  # ingest/transcribe/...
    Column("status", String, nullable=False),  # queued/running/succeeded/failed
    Column("payload", JSON, nullable=True),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
)

# API keys (EPIC-05)
api_keys = Table(
    "api_keys",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("key_hash", String, nullable=False, unique=True),
    Column("status", String, nullable=False),  # active/revoked
    Column("scopes", JSON, nullable=True),  # optional v1
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column("last_used_at", DateTime(timezone=True), nullable=True),
)
