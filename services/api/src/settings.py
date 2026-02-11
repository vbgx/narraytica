from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_", extra="ignore")

    env: str = "local"
    log_level: str = "info"

    # Postgres DSN for local dev
    database_url: str = "postgresql+psycopg://narralytica:narralytica@localhost:5432/narralytica"


settings = Settings()

# ---- OpenSearch (EPIC 00 / 00.07) ----
OPENSEARCH_TIMEOUT_SECONDS: int = 2
OPENSEARCH_BOOTSTRAP_ENABLED: bool = True

# Naming conventions:
# - template: narralytica-videos-template
# - index:    narralytica-videos-v1 (future: -v2, etc.)
OPENSEARCH_VIDEOS_TEMPLATE_NAME: str = "narralytica-videos-template"
OPENSEARCH_VIDEOS_INDEX: str = "narralytica-videos-v1"
