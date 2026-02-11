from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_", extra="ignore")

    env: str = "local"
    log_level: str = "info"

    # Postgres DSN for local dev
    database_url: str = "postgresql+psycopg://narralytica:narralytica@localhost:5432/narralytica"


settings = Settings()
