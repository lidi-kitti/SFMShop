from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Тестовые данные (в реальном приложении — БД)
products_data = [
    {"id": 1, "name": "Ноутбук", "price": 50000, "quantity": 10},
    {"id": 2, "name": "Мышь", "price": 1500, "quantity": 20},
    {"id": 3, "name": "Клавиатура", "price": 3000, "quantity": 15},
]

users_data = [
    {"id": 1, "name": "Иван", "email": "ivan@test.ru"},
    {"id": 2, "name": "Мария", "email": "maria@test.ru"},
]


class UserCreate(BaseModel):
    name: str
    email: str


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в SFMShop API"}


@app.get("/products")
def get_products():
    """Получить список товаров."""
    return products_data


@app.get("/products/{product_id}")
def get_product(product_id: int):
    """Получить товар по ID."""
    for product in products_data:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Товар не найден")


@app.get("/users")
def get_users():
    """Получить список пользователей."""
    return users_data


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Получить пользователя по ID."""
    for user in users_data:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.post("/users")
def create_user(user: UserCreate):
    """Создать нового пользователя."""
    new_user = {
        "id": len(users_data) + 1,
        "name": user.name,
        "email": user.email,
    }
    users_data.append(new_user)
    return new_user


@app.post("/orders")
def create_order(order: OrderCreate):
    """Создать заказ."""
    return {
        "id": 5,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "message": "Заказ создан",
    }
