from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки из окружения. Один конфиг на весь проект."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://postgres:user@localhost:5432/sfmshop"
    secret_key: str = Field(
        default="change-me",
        validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET_KEY"),
    )
    redis_url: str = "redis://localhost:6379/0"
    debug: bool = True
    max_connections: int = 10
    redis_host: str = "localhost"
    redis_port: int = 6379
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "sfmshop"
    db_user: str = "postgres"
    db_password: str = "user"
    db_primary_host: str = "localhost"
    db_replica_host: str = "localhost"
    db_replica_port: int = 5432
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    anthropic_api_key: str = ""
    sentry_dsn: str = ""


settings = Settings()
