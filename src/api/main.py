from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.models.product import Product
from src.models.order import Order
from src.models.user import User
from src.database.connection import (
    connect_to_db,
    get_all_products,
    get_product_by_id,
    get_user_by_id,
    create_order as db_create_order,
    create_user as db_create_user,
    update_product as db_update_product,
    delete_product as db_delete_product,
)

conn = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global conn
    conn = connect_to_db()
    yield
    if conn:
        conn.close()


app = FastAPI(lifespan=lifespan)


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class UserCreate(BaseModel):
    name: str
    email: str


class ProductUpdate(BaseModel):
    name: str = None
    price: float = None
    quantity: int = None


def _product_to_dict(data):
    product = Product(data[1], float(data[2]), data[3])
    product.id = data[0]
    return product.__dict__


@app.get("/products")
def get_products(limit: int = 10, offset: int = 0):
    try:
        products_data = get_all_products(conn)

        products = []
        for data in products_data:
            products.append(_product_to_dict(data))

        total = len(products)
        paginated_products = products[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "products": paginated_products,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.get("/products/{product_id}")
def get_product(product_id: int):
    """Получить товар по ID"""
    try:
        data = get_product_by_id(conn, product_id)
        if not data:
            raise HTTPException(status_code=404, detail="Товар не найден")
        return _product_to_dict(data)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.post("/orders", status_code=201)
def create_order(order: OrderCreate):
    try:
        user_data = get_user_by_id(conn, order.user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        product_data = get_product_by_id(conn, order.product_id)
        if not product_data:
            raise HTTPException(status_code=404, detail="Товар не найден")

        user = User(user_data["name"], user_data["email"])
        product = Product(
            product_data[1],
            float(product_data[2]),
            order.quantity,
        )

        order_obj = Order(user, [product])
        total = order_obj.calculate_total()

        order_id = db_create_order(conn, order.user_id, total)
        if order_id is None:
            raise HTTPException(status_code=500, detail="Ошибка сервера")

        return {
            "id": order_id,
            "user_id": order.user_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "total": float(total),
            "message": "Заказ создан",
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.put("/products/{product_id}")
def update_product_endpoint(product_id: int, product_data: dict):
    try:
        existing = get_product_by_id(conn, product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Товар не найден")

        updated = db_update_product(conn, product_id, product_data)
        if not updated:
            raise HTTPException(status_code=500, detail="Ошибка сервера")

        return {"id": product_id, "message": "Товар обновлен", **_product_to_dict(updated)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.delete("/products/{product_id}")
def delete_product_endpoint(product_id: int):
    try:
        existing = get_product_by_id(conn, product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Товар не найден")

        deleted = db_delete_product(conn, product_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Ошибка сервера")

        return {"message": "Товар удален"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.get("/users/{user_id}")
def get_user(user_id: int):
    try:
        user_data = get_user_by_id(conn, user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user_data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.post("/users", status_code=201)
def create_user_endpoint(user: UserCreate):
    """Создать нового пользователя"""
    try:
        new_user = User(user.name, user.email)
        db_create_user(conn, new_user.name, new_user.email)
        return {
            "name": new_user.name,
            "email": new_user.email,
            "message": "Пользователь создан",
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


def test_api():
    """Тестирование API"""
    with TestClient(app) as client:
        _run_api_tests(client)


def _run_api_tests(client):
    response = client.get("/products")
    assert response.status_code == 200
    print("GET /products: OK")

    response = client.get("/products?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "products" in data
    print("GET /products с пагинацией: OK")

    response = client.get("/products/1")
    assert response.status_code == 200
    print("GET /products/1: OK")

    response = client.get("/products/999")
    assert response.status_code == 404
    print("GET /products/999 (404): OK")

    response = client.post("/orders", json={
        "user_id": 1,
        "product_id": 2,
        "quantity": 1,
    })
    assert response.status_code == 201
    print("POST /orders: OK")

    response = client.put("/products/1", json={
        "name": "Ноутбук обновленный",
        "price": 45000,
    })
    assert response.status_code == 200
    print("PUT /products/1: OK")

    response = client.delete("/products/1")
    assert response.status_code == 200
    print("DELETE /products/1: OK")

    print("\nВсе тесты пройдены успешно!")



if __name__ == "__main__":
    test_api()
