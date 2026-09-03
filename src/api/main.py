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

from dotenv import load_dotenv

load_dotenv(_project_root / ".env")

import asyncio
import json
import os
from contextlib import asynccontextmanager
from decimal import Decimal
from urllib.parse import quote_plus

from typing import Annotated, Optional

import asyncpg
import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.database.models import get_session, get_user_orders_orm, Product, User, Order, OrderItem
from src.services.cache_service import CacheService
from src.services.async_service import process_orders_async


http_client: httpx.AsyncClient | None = None
redis_client: aioredis.Redis | None = None
pg_pool: asyncpg.Pool | None = None


def _asyncpg_dsn(read_only=True):
    host = os.getenv("DB_REPLICA_HOST" if read_only else "DB_PRIMARY_HOST", "localhost")
    port = os.getenv("DB_REPLICA_PORT" if read_only else "DB_PORT", "5433" if read_only else "5432")
    user = quote_plus(os.getenv("DB_USER", "postgres"))
    password = quote_plus(os.getenv("DB_PASSWORD", "user") or "")
    db_name = os.getenv("DB_NAME", "sfmshop")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


async def _create_pg_pool():
    """Пул к replica; если она недоступна — к primary."""
    replica_dsn = _asyncpg_dsn(read_only=True)
    primary_dsn = _asyncpg_dsn(read_only=False)
    try:
        return await asyncpg.create_pool(replica_dsn, timeout=5)
    except Exception:
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
bearer_scheme = HTTPBearer(auto_error=False)

CONTENT_TYPE_JSON = "application/json"
CACHE_PUBLIC = f"public, max-age={CacheService.TTL}"
CACHE_PRIVATE_NO_STORE = "private, no-store"
CACHE_NO_STORE = "no-store"


def api_response(content, status_code=200, cache_control=CACHE_NO_STORE):
    """JSON-ответ с Content-Type и Cache-Control."""
    return JSONResponse(
        content=content,
        status_code=status_code,
        media_type=CONTENT_TYPE_JSON,
        headers={"Cache-Control": cache_control},
    )


@app.middleware("http")
async def set_default_headers(request: Request, call_next):
    """Гарантирует Content-Type и Cache-Control, если endpoint их не задал."""
    response = await call_next(request)
    if "content-type" not in response.headers:
        response.headers["Content-Type"] = CONTENT_TYPE_JSON
    if "cache-control" not in response.headers:
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            response.headers["Cache-Control"] = CACHE_NO_STORE
        else:
            response.headers["Cache-Control"] = "no-cache"
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    headers = {"Cache-Control": CACHE_NO_STORE}
    if exc.headers:
        headers.update(exc.headers)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        media_type=CONTENT_TYPE_JSON,
        headers=headers,
    )


def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    """Проверяет Authorization: Bearer <session_id> по сессии в Redis."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Требуется заголовок Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session = cache_service.get_user_session(credentials.credentials)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Сессия недействительна или истекла",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session


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


class LoginRequest(BaseModel):
    email: str = Field(max_length=100)


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    user_id: int
    items: list[OrderItemCreate] = Field(min_length=1)
    status: str = Field(default="pending", max_length=20)


class ProductCreate(BaseModel):
    name: str = Field(max_length=100)
    price: Decimal = Field(gt=0)
    stock: int = Field(gt=0)

class ProductUpdate(BaseModel):
    name: str = Field(max_length=100)
    price: Decimal = Field(gt=0)
    stock: int = Field(gt=0)


def _product_to_dict(product):
    return {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "stock": product.stock,
    }


def _order_to_dict(order, include_items=False):
    data = {
        "id": order.id,
        "user_id": order.user_id,
        "total": float(order.total),
        "status": order.status,
        "created_at": order.order_date.isoformat() if order.order_date else None,
    }
    if include_items:
        data["items"] = [
            {
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else None,
                "quantity": item.quantity,
                "price": float(item.price),
            }
            for item in order.items
        ]
    return data


@app.get("/", status_code=200)
def read_root():
    return api_response(
        {"message": "Добро пожаловать в SFMShop API"},
        cache_control="no-cache",
    )


@app.post("/login", status_code=200)
def login(body: LoginRequest, db=Depends(get_db)):
    """Создать сессию: Authorization: Bearer <access_token>."""
    try:
        user = db.execute(select(User).where(User.email == body.email)).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Неверный email",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = cache_service.create_user_session(user.id)
        return api_response(
            {
                "access_token": token,
                "token_type": "Bearer",
                "user_id": user.id,
            },
            cache_control=CACHE_NO_STORE,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.get("/products", status_code=200)
def get_products(db=Depends(get_read_db)):
    """Получить список товаров."""
    try:
        cached_products = cache_service.get_products()
        if cached_products:
            return api_response(cached_products, cache_control=CACHE_PUBLIC)
        products = db.execute(select(Product)).scalars().all()
        products_data = [_product_to_dict(p) for p in products]
        cache_service.set_products(products_data)
        return api_response(products_data, cache_control=CACHE_PUBLIC)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить список товаров")


@app.get("/products/{product_id}", status_code=200)
def get_product(product_id: int, db=Depends(get_read_db)):
    """Получить товар по ID."""
    try:
        cached_product = cache_service.get_product(product_id)
        if cached_product:
            return api_response(cached_product, cache_control=CACHE_PUBLIC)
        product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")
        product_data = _product_to_dict(product)
        cache_service.set_product(product_id, product_data)
        return api_response(product_data, cache_control=CACHE_PUBLIC)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.post("/products", status_code=201)
def create_product(
    product: ProductCreate,
    db=Depends(get_db),
    session=Depends(require_auth),
):
    """Создать новый товар."""
    try:
        new_product = Product(name=product.name, price=product.price, stock=product.stock)
        db.add(new_product)
        db.commit()
        cache_service.invalidate_products()
        return api_response(_product_to_dict(new_product), status_code=201, cache_control=CACHE_NO_STORE)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось создать товар")


@app.put("/products/{product_id}", status_code=200)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db=Depends(get_db),
    session=Depends(require_auth),
):
    """Полностью обновить товар."""
    try:
        existing = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
        if not existing:
            raise HTTPException(status_code=404, detail="Товар не найден")
        existing.name = product.name
        existing.price = product.price
        existing.stock = product.stock
        db.commit()
        cache_service.invalidate_products()
        cache_service.invalidate_product(product_id)
        return api_response(_product_to_dict(existing), cache_control=CACHE_NO_STORE)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.delete("/products/{product_id}", status_code=200)
def delete_product(
    product_id: int,
    db=Depends(get_db),
    session=Depends(require_auth),
):
    """Удалить товар по ID."""
    try:
        existing = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
        if not existing:
            raise HTTPException(status_code=404, detail="Товар не найден")
        db.delete(existing)
        db.commit()
        cache_service.invalidate_products()
        cache_service.invalidate_product(product_id)
        return api_response(
            {"message": f"Товар с id={product_id} удалён"},
            cache_control=CACHE_NO_STORE,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.get("/users", status_code=200)
def get_users(db=Depends(get_read_db), session=Depends(require_auth)):
    """Получить список пользователей."""
    try:
        cached_users = cache_service.get_users()
        if cached_users:
            return api_response(cached_users, cache_control=CACHE_PRIVATE_NO_STORE)
        users = db.execute(select(User)).scalars().all()
        users_data = [
            {"id": u.id, "name": u.name, "email": u.email}
            for u in users
        ]
        cache_service.set_users(users_data)
        return api_response(users_data, cache_control=CACHE_PRIVATE_NO_STORE)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить список пользователей")


@app.get("/users/{user_id}", status_code=200)
def get_user(user_id: int, db=Depends(get_read_db), session=Depends(require_auth)):
    """Получить пользователя по ID."""
    try:
        cached_user = cache_service.get_user(user_id)
        if cached_user:
            return api_response(cached_user, cache_control=CACHE_PRIVATE_NO_STORE)
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        user_data = {"id": user.id, "name": user.name, "email": user.email}
        cache_service.set_user(user_id, user_data)
        return api_response(user_data, cache_control=CACHE_PRIVATE_NO_STORE)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.get("/users/{user_id}/orders", status_code=200)
def get_user_orders(user_id: int, db=Depends(get_read_db), session=Depends(require_auth)):
    """Получить заказы пользователя."""
    try:
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        orders = get_user_orders_orm(db, user_id)
        return api_response(
            {
                "user_id": user.id,
                "user_name": user.name,
                "orders": [_order_to_dict(order, include_items=True) for order in orders],
            },
            cache_control=CACHE_PRIVATE_NO_STORE,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.post("/users", status_code=201)
def create_user(user: UserCreate, db=Depends(get_db)):
    """Создать нового пользователя."""
    try:
        new_user = User(name=user.name, email=user.email, balance=user.balance)
        db.add(new_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось создать пользователя")
    cache_service.invalidate_users()
    return api_response(
        {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "balance": float(new_user.balance),
        },
        status_code=201,
        cache_control=CACHE_NO_STORE,
    )


@app.get("/orders", status_code=200)
def get_orders(
    user_id: int | None = None,
    db=Depends(get_read_db),
    session=Depends(require_auth),
):
    """Получить список заказов."""
    try:
        query = select(Order)
        if user_id is not None:
            query = query.where(Order.user_id == user_id)
        orders = db.execute(query.order_by(Order.order_date.desc())).scalars().all()
        return api_response(
            [_order_to_dict(order) for order in orders],
            cache_control=CACHE_PRIVATE_NO_STORE,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить список заказов")


@app.post("/orders", status_code=201)
def create_order(
    order: OrderCreate,
    db=Depends(get_db),
    session=Depends(require_auth),
):
    """Создать заказ: заказ + позиции + списание остатка в одной транзакции."""
    try:
        if session.get("user_id") != order.user_id:
            raise HTTPException(status_code=403, detail="Заказ можно создать только от своего имени")

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
                    product=product,
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

        return api_response(
            _order_to_dict(new_order, include_items=True),
            status_code=201,
            cache_control=CACHE_NO_STORE,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось создать заказ")


async def get_db_async():
    """Соединение из пула replica (чтение)."""
    async with pg_pool.acquire() as conn:
        yield conn


@app.get("/api/products/{product_id}/full", status_code=200)
async def get_product_full(product_id: int, conn=Depends(get_db_async)):
    """Полная информация о товаре из трёх источников."""
    try:
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

        return api_response(
            {
                **product,
                "price": float(product["price"]),
                "reviews": reviews,
                "views": views,
            },
            cache_control="public, max-age=600",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.post("/orders/process", status_code=200)
async def process_orders_endpoint(
    order_ids: Annotated[list[int], Field(min_length=1)],
    session=Depends(require_auth),
):
    """Параллельная обработка заказов. Ответ после завершения."""
    try:
        results = await process_orders_async(order_ids)
        return api_response(
            {
                "status": "success",
                "processed": len(results),
                "results": results,
            },
            cache_control=CACHE_NO_STORE,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.post("/orders/process-background", status_code=200)
async def process_orders_background(
    order_ids: Annotated[list[int], Field(min_length=1)],
    background_tasks: BackgroundTasks,
    session=Depends(require_auth),
):
    """Принять список заказов и обработать после ответа."""
    background_tasks.add_task(process_orders_async, order_ids)
    return api_response(
        {
            "status": "accepted",
            "message": "Обработка заказов запущена в фоне",
        },
        cache_control=CACHE_NO_STORE,
    )

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


