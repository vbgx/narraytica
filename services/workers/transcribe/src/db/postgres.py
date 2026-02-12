import os

import psycopg


def get_db_conn():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is required")
    return psycopg.connect(dsn)
