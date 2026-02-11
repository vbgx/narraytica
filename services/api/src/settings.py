from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "local"
    log_level: str = "info"

    service_name: str = "narralytica-api"

    # telemetry toggles (runtime)
    otel_enabled: bool = True
    metrics_enabled: bool = True

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"


settings = Settings()


# --- OpenTelemetry (optional) ---
# NOTE: keep it opt-in for local dev. Enable only when collector is running.
# Example: OTEL_ENABLED=true OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

