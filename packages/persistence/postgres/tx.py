from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def transaction(conn) -> Iterator:
    """
    Explicit transaction scope.

    Usage:
        with transaction(conn):
            ...
    """
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
