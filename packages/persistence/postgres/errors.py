class PersistenceError(Exception):
    pass


class NotFound(PersistenceError):
    pass


class Conflict(PersistenceError):
    pass


class PreconditionFailed(PersistenceError):
    pass


class RetryableDbError(PersistenceError):
    pass


def map_db_error(exc: Exception) -> Exception:
    """
    Driver -> normalized error mapping.
    Extend progressively.
    """
    return exc
