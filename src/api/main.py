from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class UserCreate(BaseModel):
    name: str
    email: str

app = FastAPI()

# Тестовые данные
products_data = [
    {"id": 1, "name": "Ноутбук", "price": 50000, "quantity": 10},
    {"id": 2, "name": "Мышь", "price": 1500, "quantity": 20},
    {"id": 3, "name": "Клавиатура", "price": 3000, "quantity": 15}
]

users_data = [
    {"id": 1, "name": "Иван", "email": "ivan@test.ru"},
    {"id": 2, "name": "Мария", "email": "maria@test.ru"}
]

@app.get("/products")
def get_products(limit: int = 10, offset: int = 0):
    products = [
        {"id": 1, "name": "Ноутбук", "price": 50000},
        {"id": 2, "name": "Мышь", "price": 1500}
        ]
    return {
        "limit": limit,
        "offset": offset,
        "products": products[offset:offset+limit]
        }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    """Получить товар по ID"""
    for product in products_data:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Товар не найден")

@app.post("/orders")
def create_order(order: OrderCreate):
    return {
        "id": 5,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "message": "Заказ создан"
        }

@app.get("/users")
def get_users():
    return users_data

@app.get("/users/{users_id}")
def get_user(user_id:int):
    for user in users_data:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Пользователь не найден")

@app.post("/users")
def create_user(user: UserCreate):
    """Создать нового пользователя"""
    new_user = {
        "id": len(users_data) + 1,
        "name": user.name,
        "email": user.email
    }
    users_data.append(new_user)
    return new_user