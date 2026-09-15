import json
from typing import Literal

import anthropic
from pydantic import BaseModel

from src.core.config import settings


async_client = anthropic.AsyncAnthropic(
    api_key=settings.anthropic_api_key,
    )

MODERATION_PROMPT = """Ты -- модератор отзывов интернет-магазина.

Проанализируй отзыв и верни JSON:
{
    "sentiment": "positive" | "neutral" | "negative",
    "is_spam": true/false (ссылки, капслок, повторы, рекламный текст),
    "has_profanity": true/false,
    "rejection_reason": "причина" или null,
    "clean_text": "очищенный текст" или null (если нужна правка)
    }

Критерии спама: ссылки, email, телефоны в тексте, капслок >50%, повторяющиеся символы/слова, рекламные призывы.
Верни ТОЛЬКО JSON."""


class ModerationResult(BaseModel):
    is_approved: bool
    sentiment: Literal[
        "positive", "neutral", "negative"
        ]
    is_spam: bool
    has_profanity: bool
    rejection_reason: str | None = None
    clean_text: str | None = None


async def moderate_review(
    text: str,
    ) -> ModerationResult:
    """Модерация отзыва."""
    response = await async_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        temperature=0,
        system=MODERATION_PROMPT,
        messages=[
        {"role": "user", "content": text}
        ],
        )
    data = json.loads(response.content[0].text)

    # Решение о публикации -- на стороне кода
    is_approved = not (
        data["is_spam"] or data["has_profanity"]
        )

    return ModerationResult(
        is_approved=is_approved,
        sentiment=data["sentiment"],
        is_spam=data["is_spam"],
        has_profanity=data["has_profanity"],
        rejection_reason=data.get(
        "rejection_reason"
        ),
        clean_text=data.get("clean_text"),
        )