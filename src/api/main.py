# Процесс загрузки страницы проекта SFMShop:
#
# 1. DNS-запрос:
# - Браузер преобразует доменное имя в IP-адрес
# - Возможная задержка: медленный DNS-сервер
# - Оптимизация: использование быстрых DNS-серверов, кэширование DNS
#
# 2. TCP-подключение:
# - Установка соединения с сервером (TCP handshake)
# - Для HTTPS: дополнительный TLS handshake
# - Возможная задержка: медленное подключение, географическое расстояние
# - Оптимизация: использование CDN, оптимизация сервера
#
# 3. HTTP-запрос:
# - Клиент отправляет запрос к API (например, GET /api/products)
# - Возможная задержка: большой размер запроса
# - Оптимизация: минимизация размера запроса
#
# 4. Обработка на сервере:
# - FastAPI получает запрос и обрабатывает его
# - Запрос к БД для получения данных
# - Возможная задержка: медленные запросы к БД, отсутствие кэширования
# - Оптимизация: индексы в БД, кэширование через Redis, асинхронная обработка
#
# 5. HTTP-ответ:
# - Сервер отправляет данные клиенту
# - Возможная задержка: большой размер ответа, отсутствие сжатия
# - Оптимизация: сжатие данных (gzip), пагинация, минимизация JSON
#
# 6. Рендеринг на клиенте:
# - Браузер обрабатывает ответ и отображает данные
# - Возможная задержка: медленный JavaScript, большие данные
# - Оптимизация: оптимизация фронтенда, ленивая загрузка данных
#
# Возможные узкие места в проекте SFMShop:
# - Медленные запросы к PostgreSQL (нужны индексы)
# - Отсутствие кэширования (нужен Redis)
# - Синхронная обработка вместо асинхронной (нужен async/await)
# - Большой размер JSON-ответов (нужна пагинация)


import sys
from pathlib import Path

# При запуске файла напрямую (python src/api/main.py) в sys.path
# попадает src/api, а не корень проекта — пакет src тогда не находится.
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import asyncio
import json
import os
from contextlib import asynccontextmanager
from decimal import Decimal

from typing import Annotated

import asyncpg
import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.database.models import get_session, Product, User, Order, OrderItem
from src.services.cache_service import CacheService
from src.services.async_service import process_orders_async


http_client: httpx.AsyncClient | None = None
redis_client: aioredis.Redis | None = None
pg_pool: asyncpg.Pool | None = None


def _asyncpg_dsn(read_only=True):
    host = os.getenv("DB_REPLICA_HOST" if read_only else "DB_PRIMARY_HOST", "localhost")
    port = os.getenv("DB_REPLICA_PORT" if read_only else "DB_PORT", "5433" if read_only else "5432")
    return (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{host}:{port}/{os.getenv('DB_NAME', 'sfmshop')}"
    )


async def _create_pg_pool():
    """Пул к replica; если она недоступна — к primary."""
    replica_dsn = _asyncpg_dsn(read_only=True)
    primary_dsn = _asyncpg_dsn(read_only=False)
    try:
        return await asyncpg.create_pool(replica_dsn, timeout=5)
    except OSError:
        if replica_dsn == primary_dsn:
            raise
        return await asyncpg.create_pool(primary_dsn, timeout=5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client, redis_client, pg_pool
    http_client = httpx.AsyncClient()
    redis_client = aioredis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True,
    )
    try:
        pg_pool = await _create_pg_pool()
    except Exception:
        await http_client.aclose()
        await redis_client.aclose()
        raise
    yield
    await http_client.aclose()
    await redis_client.aclose()
    await pg_pool.close()


app = FastAPI(lifespan=lifespan)
cache_service = CacheService()


def get_db():
    """Сессия к primary: закрывается после запроса, при ошибке — rollback."""
    db = get_session()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_read_db():
    """Сессия к replica для чтения."""
    db = get_session(read_only=True)
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)
    balance: Decimal = Decimal("0")


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    user_id: int
    items: list[OrderItemCreate] = Field(min_length=1)
    status: str = Field(default="pending", max_length=20)


@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в SFMShop API"}


@app.get("/products")
def get_products(db=Depends(get_read_db)):
    """Получить список товаров."""
    cached_products = cache_service.get_products()
    if cached_products:
        return cached_products
    products = db.execute(select(Product)).scalars().all()
    products_data = [
        {"id": p.id, "name": p.name, "price": float(p.price), "stock": p.stock}
        for p in products
    ]
    cache_service.set_products(products_data)
    return products_data


@app.get("/products/{product_id}")
def get_product(product_id: int, db=Depends(get_read_db)):
    """Получить товар по ID."""
    cached_product = cache_service.get_product(product_id)
    if cached_product:
        return cached_product
    product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    product_data = {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "stock": product.stock,
    }
    cache_service.set_product(product_id, product_data)
    return product_data


@app.get("/users")
def get_users(db=Depends(get_read_db)):
    """Получить список пользователей."""
    cached_users = cache_service.get_users()
    if cached_users:
        return cached_users
    users = db.execute(select(User)).scalars().all()
    users_data = [
        {"id": u.id, "name": u.name, "email": u.email}
        for u in users
    ]
    cache_service.set_users(users_data)
    return users_data


@app.get("/users/{user_id}")
def get_user(user_id: int, db=Depends(get_read_db)):
    """Получить пользователя по ID."""
    cached_user = cache_service.get_user(user_id)
    if cached_user:
        return cached_user
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user_data = {"id": user.id, "name": user.name, "email": user.email}
    cache_service.set_user(user_id, user_data)
    return user_data


@app.post("/users")
def create_user(user: UserCreate, db=Depends(get_db)):
    """Создать нового пользователя."""
    new_user = User(name=user.name, email=user.email, balance=user.balance)
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
    cache_service.invalidate_users()
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "balance": float(new_user.balance),
    }


@app.post("/orders")
def create_order(order: OrderCreate, db=Depends(get_db)):
    """Создать заказ: заказ + позиции + списание остатка в одной транзакции."""
    user = db.execute(select(User).where(User.id == order.user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    new_order = Order(user_id=user.id, total=Decimal("0"), status=order.status)
    total = Decimal("0")
    touched_product_ids = []

    for item in order.items:
        product = db.execute(
            select(Product).where(Product.id == item.product_id).with_for_update()
        ).scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар {item.product_id} не найден")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Недостаточно товара: {product.name}")

        total += product.price * item.quantity
        new_order.items.append(
            OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                price=product.price,
            )
        )
        product.stock -= item.quantity
        touched_product_ids.append(product.id)

    new_order.total = total
    db.add(new_order)
    db.commit()

    cache_service.invalidate_products()
    for product_id in set(touched_product_ids):
        cache_service.invalidate_product(product_id)

    return {
        "id": new_order.id,
        "user_id": new_order.user_id,
        "total": float(new_order.total),
        "status": new_order.status,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": float(item.price),
            }
            for item in new_order.items
        ],
    }


async def get_db_async():
    """Соединение из пула replica (чтение)."""
    async with pg_pool.acquire() as conn:
        yield conn


@app.get("/api/products/{product_id}/full")
async def get_product_full(product_id: int, conn=Depends(get_db_async)):
    """Полная информация о товаре из трёх источников."""

    async def fetch_product():
        row = await conn.fetchrow(
            "SELECT id, name, price, stock FROM products WHERE id = $1",
            product_id,
        )
        return dict(row) if row else None

    async def fetch_reviews():
        cache_key = f"cache:reviews:{product_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        try:
            response = await http_client.get(
                f"https://api.reviews.sfmshop.ru/product/{product_id}",
                timeout=3.0,
            )
            response.raise_for_status()
            reviews = response.json()
            await redis_client.setex(cache_key, 600, json.dumps(reviews))
            return reviews
        except httpx.HTTPError:
            return []

    async def count_view():
        return await redis_client.incr(f"views:product:{product_id}")

    product, reviews = await asyncio.gather(
        fetch_product(),
        fetch_reviews(),
    )

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    views = await count_view()

    return {
        **product,
        "price": float(product["price"]),
        "reviews": reviews,
        "views": views,
    }


@app.post("/orders/process")
async def process_orders_endpoint(order_ids: Annotated[list[int], Field(min_length=1)]):
    """Параллельная обработка заказов. Ответ после завершения."""
    results = await process_orders_async(order_ids)
    return {
        "status": "success",
        "processed": len(results),
        "results": results,
    }


@app.post("/orders/process-background")
async def process_orders_background(
    order_ids: Annotated[list[int], Field(min_length=1)],
    background_tasks: BackgroundTasks,
):
    """Принять список заказов и обработать после ответа."""
    background_tasks.add_task(process_orders_async, order_ids)
    return {
        "status": "accepted",
        "message": "Обработка заказов запущена в фоне",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import time
import requests

def measure_api_performance(url):
    """Измерить производительность API endpoint"""
    results = {}

    # 1. Измерение DNS-запроса
    import socket
    start = time.time()
    hostname = url.split('/')[2]
    ip = socket.gethostbyname(hostname)
    dns_time = time.time() - start
    results['dns'] = dns_time

    # 2. Измерение полного времени запроса
    start = time.time()
    response = requests.get(url)
    total_time = time.time() - start
    results['total'] = total_time

    # 3. Время до получения заголовков ответа (сеть + сервер)
    # Внимание: response.elapsed - это не чистое время обработки на сервере,
    # а время от отправки запроса до получения заголовков (включает сеть).
    # Чистое серверное время так не измерить - нужны серверные метрики или заголовок Server-Timing.
    server_time = response.elapsed.total_seconds()
    results['server'] = server_time

    # 4. Размер ответа
    results['size'] = len(response.content)

    return results
# Использование
url = "https://sfmshop.com/api/products"
diagnosis = measure_api_performance(url)
print(f"DNS: {diagnosis['dns']} сек")
print(f"Сервер: {diagnosis['server']} сек")
print(f"Всего: {diagnosis['total']} сек")
print(f"Размер: {diagnosis['size']} байт")


