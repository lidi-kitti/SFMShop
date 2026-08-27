# Файл src/services/cache_service.py
import json
import sys
from pathlib import Path
import uuid
import redis

_src_root = Path(__file__).resolve().parent.parent
if str(_src_root) not in sys.path:
    sys.path.insert(0, str(_src_root))

from database.queries import get_all_products, get_product_by_id

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
    protocol=2,
)

def create_user_session(user_id):
    """Создание сессии пользователя"""
    session_id = str(uuid.uuid4())
    redis_client.setex(f"session:{session_id}", 86400, json.dumps({"user_id": user_id}))
    return session_id

def get_user_session(session_id):
    """Получение сессии пользователя"""
    session = redis_client.get(f"session:{session_id}")
    if session:
        return json.loads(session)
    return None

def invalidate_user_session(session_id):
    """Инвалидация сессии пользователя"""
    redis_client.delete(f"session:{session_id}")

def get_cached_products():
    """Получение товаров с кэшированием"""
    cache_key = "products:all"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    products = get_all_products()
    redis_client.setex(cache_key, 3600, json.dumps(products))
    return products

def get_cached_product(product_id):
    """Получение товара по ID с кэшированием"""
    cache_key = f"product:{product_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    product = get_product_by_id(product_id)
    if product:
        redis_client.setex(cache_key, 3600, json.dumps(product))
    return product

def invalidate_products_cache():
    """Инвалидация кэша товаров"""
    redis_client.delete("products:all")
    print("Кэш товаров очищен")

def invalidate_product_cache(product_id):
    """Инвалидация кэша товара"""
    redis_client.delete(f"product:{product_id}")
    print(f"Кэш товара {product_id} очищен")

# Тестирование
if __name__ == "__main__":
    # Первый запрос - из БД
    products1 = get_cached_products()

    # Второй запрос - из кэша
    products2 = get_cached_products()

    # Инвалидация кэша# Тест кэширования товара
    product = get_cached_product(1)
    print(f"Товар: {product}")
    
    # Тест сессий
    session_token = create_user_session(user_id=1)
    print(f"Сессия создана: {session_token}")
    
    session = get_user_session(session_token)
    print(f"Сессия: {session}")