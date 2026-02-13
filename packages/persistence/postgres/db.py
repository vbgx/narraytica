from collections.abc import Iterator
from contextlib import contextmanager

import psycopg


def get_connection(dsn: str):
    """
    Single DB entrypoint.
    No global state, no hidden pool.
    """
    return psycopg.connect(dsn)


@contextmanager
def connection(dsn: str) -> Iterator[psycopg.Connection]:
    conn = get_connection(dsn)
    try:
        yield conn
    finally:
        conn.close()
