from __future__ import annotations

import json
import logging
import os
import sys
import time
from typing import Any, Mapping, Optional


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # extra fields (safe)
        for k in ("request_id", "path", "method", "status_code", "duration_ms"):
            v = getattr(record, k, None)
            if v is not None:
                base[k] = v

        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(base, ensure_ascii=False)


def setup_logging(level: Optional[str] = None) -> None:
    lvl = (level or os.getenv("LOG_LEVEL", "info")).upper()
    root = logging.getLogger()
    root.setLevel(lvl)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    # reset handlers (avoid duplicates in reload)
    root.handlers = [handler]


def log_extra(logger: logging.Logger, extra: Mapping[str, Any]) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logger, dict(extra))
