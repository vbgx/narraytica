from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from db.schema import metadata

# With prepend_sys_path = services/api/src these imports resolve.
from settings import settings
from sqlalchemy import create_engine, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata


def get_url() -> str:
    url = os.getenv("API_DATABASE_URL") or settings.database_url
    # Hard log so we can see what Alembic is actually using
    print(f"[alembic] using API_DATABASE_URL={url}")
    return url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()

    engine = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
