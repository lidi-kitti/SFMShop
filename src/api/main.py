import sys
from pathlib import Path

# При запуске файла напрямую (python src/api/main.py) в sys.path
# попадает src/api, а не корень проекта — пакет src тогда не находится.
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.database.models import get_session, Product, User, Order, OrderItem
from src.services.cache_service import CacheService

app = FastAPI()
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
from fastapi import FastAPI, Depends
import asyncio
import asyncpg
import httpx
import redis.asyncio as aioredis
import json

http_client: httpx.AsyncClient | None = None
# Глобальный Redis-клиент (инициализируется при старте)
redis_client: aioredis.Redis | None = None

async def get_db_async():
    conn = await asyncpg.connect("postgresql://localhost/sfmshop")
    try:
        yield conn
    finally:
        await conn.close()


@app.get("/api/products/{product_id}/full")
async def get_product_full(product_id: int, conn=Depends(get_db_async)):
    """Полная информация о товаре из трёх источников"""
    
    async def fetch_product():
        """Товар из PostgreSQL"""
        row = await conn.fetchrow(
            "SELECT id, name, price, description FROM products WHERE id = $1",
            product_id
        )
        return dict(row) if row else None
    
    async def fetch_reviews():
        """Отзывы - сначала из кэша, потом из API"""
        cache_key = f"cache:reviews:{product_id}"
        
        # Проверяем кэш
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Загружаем из API
        try:
            response = await http_client.get(
                f"https://api.reviews.sfmshop.ru/product/{product_id}",
                timeout=3.0
            )
            response.raise_for_status()
            reviews = response.json()
            
            # Кэшируем на 10 минут
            await redis_client.setex(cache_key, 600, json.dumps(reviews))
            return reviews
        except (httpx.HTTPError, httpx.TimeoutException):
            return []
    
    async def count_view():
        """Инкремент просмотров в Redis"""
        views = await redis_client.incr(f"views:product:{product_id}")
        return views
    
    # Параллельные запросы
    product, reviews, views = await asyncio.gather(
        fetch_product(),
        fetch_reviews(),
        count_view(),
    )
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    return {
        **product,
        "price": float(product["price"]),
        "reviews": reviews,
        "views": views
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
