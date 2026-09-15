import asyncio
import json

import anthropic
import chromadb

from src.core.config import settings


PRODUCTS = [
    {"id": "1", "name": "ASUS VivoBook 15", "category": "Ноутбуки", "price": 45990, "in_stock": True, "description": "Intel Core i5, 8 ГБ RAM, 512 ГБ SSD, 15.6 дюймов"},
    {"id": "2", "name": "Samsung Galaxy A54", "category": "Смартфоны", "price": 29990, "in_stock": True, "description": "128 ГБ, камера 50 МП, AMOLED 6.4 дюйма"},
    {"id": "3", "name": "Sony WH-1000XM5", "category": "Наушники", "price": 24990, "in_stock": True, "description": "Шумоподавление, 30 часов, Bluetooth 5.3"},
    {"id": "4", "name": "Lenovo IdeaPad 3", "category": "Ноутбуки", "price": 38990, "in_stock": True, "description": "AMD Ryzen 5, 8 ГБ RAM, 256 ГБ SSD"},
    {"id": "5", "name": "Xiaomi Redmi Note 13", "category": "Смартфоны", "price": 18990, "in_stock": False, "description": "256 ГБ, камера 108 МП, AMOLED 6.67 дюйма"},
    {"id": "6", "name": "Apple MacBook Air M3", "category": "Ноутбуки", "price": 109990, "in_stock": True, "description": "Apple M3, 8 ГБ RAM, 256 ГБ SSD, 13.6 дюймов"},
    {"id": "7", "name": "JBL Tune 520BT", "category": "Наушники", "price": 3490, "in_stock": True, "description": "Bluetooth 5.3, 57 часов, складные"},
    {"id": "8", "name": "Apple iPhone 15", "category": "Смартфоны", "price": 79990, "in_stock": True, "description": "128 ГБ, камера 48 МП, Dynamic Island"},
    {"id": "9", "name": "Logitech MX Keys", "category": "Клавиатуры", "price": 8990, "in_stock": True, "description": "Беспроводная, подсветка, мультиустройство"},
    {"id": "10", "name": "Samsung Galaxy Buds3", "category": "Наушники", "price": 12990, "in_stock": False, "description": "ANC, 6 часов, IP57"},
    ]

SYSTEM = """Ты -- консультант SFMShop.
Отвечай ТОЛЬКО по предоставленному каталогу.
Указывай цены и наличие. Если товара нет -- скажи.
Кратко, по делу."""


def index_catalog(
    collection, products: list[dict],
    ) -> None:
    """Индексация каталога в ChromaDB."""
    documents = []
    metadatas = []
    ids = []

    for p in products:
        doc = (
            f"{p['name']}. {p['description']}. "
            f"Категория: {p['category']}. "
            f"Цена: {p['price']} руб. "
            f"{'В наличии' if p['in_stock'] else 'Нет в наличии'}."
            )
        documents.append(doc)
        metadatas.append({
            "name": p["name"],
            "price": p["price"],
            "category": p["category"],
            "in_stock": p["in_stock"],
            })
        ids.append(p["id"])

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        )


def smart_search(
    collection,
    query: str,
    n_results: int = 5,
    category: str | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    ) -> list[dict]:
    """Поиск с фильтрацией."""
    where_conditions = []
    if category:
        where_conditions.append(
            {"category": category}
            )
    if max_price:
        where_conditions.append(
            {"price": {"$lte": max_price}}
            )
    if in_stock_only:
        where_conditions.append(
            {"in_stock": True}
            )

    where = None
    if len(where_conditions) == 1:
        where = where_conditions[0]
    elif len(where_conditions) > 1:
        where = {"$and": where_conditions}

    kwargs = {
        "query_texts": [query],
        "n_results": n_results,
        }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)

    found = []
    for i, doc in enumerate(
        results["documents"][0]
        ):
        found.append({
            "text": doc,
            "metadata": results["metadatas"][0][i],
            })
    return found


async def answer_product_question(
    collection, client, question: str,
    ) -> str:
    """RAG-ответ на вопрос."""
    products = smart_search(
        collection, question, n_results=5,
        )

    if not products:
        return (
            "К сожалению, ничего не найдено. "
            "Обратитесь к оператору."
            )

    context_parts = []
    for i, p in enumerate(products, 1):
        m = p["metadata"]
        stock = (
            "в наличии"
            if m["in_stock"]
            else "нет в наличии"
            )
        context_parts.append(
            f"{i}. {m['name']} -- "
            f"{m['price']} руб. ({stock})"
            f"\n {p['text']}"
            )

    context = "\n".join(context_parts)

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=SYSTEM,
        messages=[
        {
        "role": "user",
        "content": (
        f"Каталог:\n{context}\n\n"
        f"Вопрос: {question}"
        ),
        }
        ],
        )
    return response.content[0].text


async def main():
    chroma = chromadb.Client()
    collection = chroma.create_collection(
        name="sfmshop_demo",
        )
    index_catalog(collection, PRODUCTS)

    ai_client = anthropic.AsyncAnthropic(
        api_key=settings.anthropic_api_key,
        )

    questions = [
        "Ноутбук для учёбы до 50 тысяч?",
        "Наушники с шумоподавлением?",
        "Что есть в наличии из смартфонов?",
        "Сравни два самых дешёвых ноутбука",
        "Есть что-нибудь от Apple?",
        ]

    for q in questions:
        print(f"\nВопрос: {q}")
        answer = await answer_product_question(
            collection, ai_client, q,
            )
        print(f"Ответ: {answer}")


if __name__ == "__main__":
    asyncio.run(main())