from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки из окружения. Секреты без реальных значений в репозитории."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://postgres:user@localhost:5432/sfmshop"
    secret_key: str = "change-me"
    redis_url: str = "redis://localhost:6379/0"
    debug: bool = True
    max_connections: int = 10
    redis_host: str = "localhost"
    redis_port: int = 6379
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    anthropic_api_key: str = ""
    sentry_dsn: str = ""


settings = Settings()
