import json

import anthropic
from pydantic import BaseModel

from src.core.config import settings


async_client = anthropic.AsyncAnthropic(
    api_key=settings.anthropic_api_key,
    )

CATEGORIES = [
    "Ноутбуки", "Смартфоны", "Планшеты",
    "Наушники", "Клавиатуры", "Мониторы",
    "Аксессуары",
    ]

CARD_PROMPT = """Ты -- SEO-копирайтер магазина электроники.
Сгенерируй карточку товара в JSON:
{
    "title": "SEO-заголовок (до 60 символов)",
    "description": "описание 2-3 предложения",
    "seo_keywords": ["5-7 ключевых слов"],
    "category": "одна из: Ноутбуки, Смартфоны, Планшеты, Наушники, Клавиатуры, Мониторы, Аксессуары"
    }
Верни ТОЛЬКО JSON."""


class ProductCard(BaseModel):
    title: str
    description: str
    seo_keywords: list[str]
    category: str


async def generate_product_card(
    name: str,
    features: list[str],
    price: float,
    ) -> ProductCard:
    """SEO-описание + категория."""
    features_text = "\n".join(
        f"- {f}" for f in features
        )
    response = await async_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        temperature=0.5,
        system=CARD_PROMPT,
        messages=[
        {
        "role": "user",
        "content": (
        f"Товар: {name}\n"
        f"Цена: {price} руб.\n"
        f"Характеристики:\n{features_text}"
        ),
        }
        ],
        )
    data = json.loads(response.content[0].text)
    # Валидация категории
    if data["category"] not in CATEGORIES:
        data["category"] = "Аксессуары"
    return ProductCard(**data)


async def categorize_batch(
    products: list[dict],
    ) -> list[str]:
    """Пакетная категоризация через Haiku."""
    items = "\n".join(
        f"{i+1}. {p['name']}: {p['description']}"
        for i, p in enumerate(products)
        )
    cats = ", ".join(CATEGORIES)

    response = await async_client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=200,
        temperature=0,
        messages=[
        {
        "role": "user",
        "content": (
        f"Категории: {cats}\n"
        f"Товары:\n{items}\n\n"
        f"Верни JSON-массив категорий "
        f"в том же порядке."
        ),
        }
        ],
        )
    categories = json.loads(
        response.content[0].text,
        )
    # Валидация каждой категории
    return [
        c if c in CATEGORIES else "Аксессуары"
        for c in categories
        ]