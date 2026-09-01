import redis.asyncio as aioredis
import json
import functools


# Глобальный Redis-клиент (инициализируется при старте)
redis_client: aioredis.Redis | None = None


async def init_redis():
    global redis_client
    redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True, encoding="utf-8", protocol=2)

def cache_async(ttl: int = 300, prefix: str = "cache"):
    """Декоратор для кэширования async-функций в Redis"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{func.__name__}:{args}:{kwargs}"
            result = await redis_client.get(key)
            if result:
                return json.loads(result)
            result = await func(*args, **kwargs)
            await redis_client.set(key, json.dumps(result), ex=ttl)
            return result
        return wrapper
    return decorator

# Пример использования
@cache_async(ttl=600, prefix="products")
async def get_product(product_id: int) -> dict:
    """Получение товара из БД (кэшируется на 10 минут)"""
    # Имитация запроса к БД
    import asyncio
    await asyncio.sleep(1)
    return {"id": product_id, "name": f"Товар {product_id}", "price": 1500}


async def main():
    await init_redis()

    # Первый вызов — загрузка из БД
    product = await get_product(42)
    print(f"Результат: {product}")

    # Второй вызов — из кэша
    product = await get_product(42)
    print(f"Результат: {product}")

    await redis_client.aclose()

import asyncio
asyncio.run(main())