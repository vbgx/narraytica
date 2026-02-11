from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Core
    env: str = "local"
    log_level: str = "info"
    service_name: str = "narralytica-api"

    # Telemetry toggles (runtime)
    otel_enabled: bool = False
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    metrics_enabled: bool = True

    # Dependencies
    # Accepts SQLAlchemy style driver too (we normalize in health/db code):
    # postgresql+psycopg://user:pass@host:port/db
    database_url: str = "postgresql+psycopg://narralytica:narralytica@127.0.0.1:15432/narralytica"
    redis_url: str = "redis://127.0.0.1:6379"

    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"


settings = Settings()
