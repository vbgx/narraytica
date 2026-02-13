from packages.persistence.postgres.tx import transaction


class DummyConn:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def test_transaction_commit():
    conn = DummyConn()
    with transaction(conn):
        pass
    assert conn.committed


def test_transaction_rollback():
    conn = DummyConn()
    try:
        with transaction(conn):
            raise RuntimeError()
    except RuntimeError:
        pass
    assert conn.rolled_back
