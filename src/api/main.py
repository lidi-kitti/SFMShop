from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.models.product import Product
from src.models.order import Order
from src.models.user import User
from src.database.connection import *


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

app = FastAPI()
conn = None

@app.on_event("startup")
async def startup():
    global conn
    conn = connect_to_db()

@app.on_event("shutdown")
async def shutdown():
    if conn:
        conn.close()

@app.get("/products")
def get_products(limit: int = 10, offset: int = 0):
    try:
        # Получить данные из БД
        products_data = get_all_products(conn)

        # Создать объекты класса Product
        products = []
        for data in products_data:
            product = Product(data[1], data[2], data[3]) # name, price, quantity
            product.id = data[0] # id
            products.append(product.__dict__)

            # Применить пагинацию
            total = len(products)
            paginated_products = products[offset:offset + limit]

            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "products": paginated_products
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
def get_product(product_id: int):
    """Получить товар по ID"""
    try:
        # Получить данные из БД
        products_data = get_all_products(conn)
        for data in products_data:
            if data[0] == product_id:
                product = Product(data[1], data[2], data[3])
                product.id = data[0]
                return product.__dict__
        raise HTTPException(status_code=404, detail="Товар не найден")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/orders", status_code=201)
def create_order(order: OrderCreate):
    try:
        new_order = Order(order.user_id, [order.product_id], order.quantity)
        create_order(conn, new_order.user_id, new_order.quantity )
        return {
            "id": 5,
            "user_id": new_order.user_id,
            "product_id": new_order.product_id,
            "quantity": new_order.quantity,
            "message": "Заказ создан"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/products/{product_id}")
def update_product(product_id: int, product_data: dict):
    try:
        # Проверить существование товара
        products_data = get_all_products(conn)
        found = False
        for data in products_data:
            if data[0] == product_id:
                found = True
                break

            if not found:
                raise HTTPException(status_code=404, detail="Товар не найден")

        # Обновить товар в БД
        update_product(conn, product_id, product_data)
        # Вернуть обновленный товар
        return {"id": product_id, "message": "Товар обновлен"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    try:
        # Проверить существование товара
        products_data = get_all_products(conn)
        found = False
        for data in products_data:
            if data[0] == product_id:
                found = True
                break

            if not found:
                raise HTTPException(status_code=404, detail="Товар не найден")

        # Удалить товар из БД
        delete_product(product_id)
        # Вернуть сообщение
        return {"message": "Товар удален"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/users")
# def get_users():
#     try:
#         return users_data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}")
def get_user(user_id: int):
    try:
        users_data = get_user_by_id(conn, user_id)
        for user in users_data:
            if user["id"] == user_id:
                return user
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    """Создать нового пользователя"""
    try:
        new_user = User(user.name, user.email)
        create_user(conn, new_user.name, new_user.email)
        return {
            "name": new_user.name,
            "email": new_user.email,
            "message": "Пользователь создан"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def test_api():
    """Тестирование API"""
    client = TestClient(app)

    # Тест GET /products
    response = client.get("/products")
    assert response.status_code == 200
    print(" GET /products: OK")

    # Тест GET /products с пагинацией
    response = client.get("/products?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "products" in data
    print(" GET /products с пагинацией: OK")

    # Тест GET /products/{id}
    response = client.get("/products/1")
    assert response.status_code == 200
    print(" GET /products/1: OK")

    # Тест GET /products/{id} - не найден
    response = client.get("/products/999")
    assert response.status_code == 404
    print(" GET /products/999 (404): OK")

    # Тест POST /orders
    response = client.post("/orders", json={
        "user_id": 1,
        "product_id": 2,
        "quantity": 1
        })
    assert response.status_code == 201
    print(" POST /orders: OK")

    # Тест PUT /products/{id}
    response = client.put("/products/1", json={
        "name": "Ноутбук обновленный",
        "price": 45000
        })
    assert response.status_code == 200
    print(" PUT /products/1: OK")

    # Тест DELETE /products/{id}
    response = client.delete("/products/1")
    assert response.status_code == 200
    print(" DELETE /products/1: OK")

    print("\n Все тесты пройдены успешно!")

if __name__ == "__main__":
    test_api()