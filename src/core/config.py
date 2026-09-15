import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Настройки из окружения. AI-сервисы читают ключ Anthropic отсюда."""

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")


settings = Settings()
