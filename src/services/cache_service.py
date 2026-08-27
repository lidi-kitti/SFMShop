# Файл src/services/cache_service.py
import json
import sys
from pathlib import Path

import redis

_src_root = Path(__file__).resolve().parent.parent
if str(_src_root) not in sys.path:
    sys.path.insert(0, str(_src_root))

from database.queries import get_all_products

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
    protocol=2,
)

def get_cached_products():
    """Получение товаров с кэшированием"""
    # Проверка кэша
    cached = redis_client.get("products:all")
    if cached:
        # Данные есть в кэше
        print("Данные из кэша Redis")
        return json.loads(cached)

    # Данных нет в кэше - получаем из БД
    print("Данные из PostgreSQL")
    products = get_all_products()

    # Сохраняем в кэш на 1 час
    redis_client.setex("products:all", 3600, json.dumps(products))

    return products

def invalidate_products_cache():
    """Инвалидация кэша товаров"""
    redis_client.delete("products:all")
    print("Кэш товаров очищен")

# Тестирование
if __name__ == "__main__":
    # Первый запрос - из БД
    products1 = get_cached_products()

    # Второй запрос - из кэша
    products2 = get_cached_products()

    # Инвалидация кэша
    invalidate_products_cache()