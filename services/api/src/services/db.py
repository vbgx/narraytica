from __future__ import annotations

"""
Compatibility shim.

Some repos import:
  from ..services.db import get_db

But the canonical DB wiring lives in:
  services/api/src/db/engine.py

This module re-exports get_conn as get_db to avoid duplication.
"""

try:
    from ..db.engine import get_conn as get_db  # type: ignore
except Exception as _err:  # pragma: no cover
    _err_repr = repr(_err)

    def get_db():  # type: ignore
        raise RuntimeError(
            "DB dependency provider not available. "
            "Expected services/api/src/db/engine.py "
            "to expose get_conn() (used as get_db shim). "
            f"Original error: {_err_repr}"
        )
