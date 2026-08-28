import json
import os
import uuid

import redis
from dotenv import load_dotenv

load_dotenv()


class CacheService:
    """Кэш Redis: каталог, пользователи и сессии. Промах обрабатывает вызывающий код."""

    PRODUCTS_KEY = "products:all"
    USERS_KEY = "users:all"
    TTL = 3600
    SESSION_TTL = 86400

    def __init__(self, host=None, port=None, db=0):
        self.client = redis.Redis(
            host=host or os.getenv("REDIS_HOST", "localhost"),
            port=int(port or os.getenv("REDIS_PORT", 6379)),
            db=db,
            decode_responses=True,
            protocol=2,
        )

    def _get_json(self, key):
        cached = self.client.get(key)
        return json.loads(cached) if cached else None

    def _set_json(self, key, value, ttl=None):
        self.client.setex(key, ttl or self.TTL, json.dumps(value))

    def get_products(self):
        return self._get_json(self.PRODUCTS_KEY)

    def set_products(self, products_data):
        self._set_json(self.PRODUCTS_KEY, products_data)

    def invalidate_products(self):
        self.client.delete(self.PRODUCTS_KEY)

    def get_product(self, product_id):
        return self._get_json(f"product:{product_id}")

    def set_product(self, product_id, product_data):
        self._set_json(f"product:{product_id}", product_data)

    def invalidate_product(self, product_id):
        self.client.delete(f"product:{product_id}")

    def get_users(self):
        return self._get_json(self.USERS_KEY)

    def set_users(self, users_data):
        self._set_json(self.USERS_KEY, users_data)

    def invalidate_users(self):
        self.client.delete(self.USERS_KEY)

    def get_user(self, user_id):
        return self._get_json(f"user:{user_id}")

    def set_user(self, user_id, user_data):
        self._set_json(f"user:{user_id}", user_data)

    def invalidate_user(self, user_id):
        self.client.delete(f"user:{user_id}")

    def create_user_session(self, user_id):
        session_id = str(uuid.uuid4())
        self._set_json(f"session:{session_id}", {"user_id": user_id}, self.SESSION_TTL)
        return session_id

    def get_user_session(self, session_id):
        return self._get_json(f"session:{session_id}")

    def invalidate_user_session(self, session_id):
        self.client.delete(f"session:{session_id}")


if __name__ == "__main__":
    cache = CacheService()

    session_id = cache.create_user_session(user_id=1)
    print(f"Сессия создана: {session_id}")
    print(f"Сессия: {cache.get_user_session(session_id)}")
