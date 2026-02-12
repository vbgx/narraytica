from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve repo root assuming this file is: services/api/src/config.py
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # Core
    env: str = Field(default="local", alias="ENV")
    log_level: str = Field(default="info", alias="LOG_LEVEL")

    # API DB
    api_database_url: str | None = Field(default=None, alias="API_DATABASE_URL")

    # API auth (EPIC-05)
    api_key_pepper: str | None = Field(default=None, alias="API_KEY_PEPPER")

    # Postgres (components)
    postgres_host: str = Field(default="127.0.0.1", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=15432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="narralytica", alias="POSTGRES_DB")
    postgres_user: str = Field(default="narralytica", alias="POSTGRES_USER")
    postgres_password: str = Field(default="narralytica", alias="POSTGRES_PASSWORD")

    # Redis / Search / Vector
    redis_url: str | None = Field(default=None, alias="REDIS_URL")
    opensearch_url: str | None = Field(default=None, alias="OPENSEARCH_URL")
    qdrant_url: str | None = Field(default=None, alias="QDRANT_URL")

    # S3 / MinIO
    s3_endpoint: str | None = Field(default=None, alias="S3_ENDPOINT")
    s3_access_key: str | None = Field(default=None, alias="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(default=None, alias="S3_SECRET_KEY")
    s3_bucket: str | None = Field(default=None, alias="S3_BUCKET")

    # OpenTelemetry (optional)
    otel_enabled: bool = Field(default=False, alias="OTEL_ENABLED")
    otel_exporter_otlp_endpoint: str = Field(
        default="http://localhost:4318", alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    service_name: str = Field(default="narralytica-api", alias="OTEL_SERVICE_NAME")

    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env.local", REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
