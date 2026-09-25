from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.limiter import limiter
from src.api.main import app
from src.api.router import ProductAPI
from src.api.schemas import ProductCreate
from src.schemas.product import ProductResponse

client = TestClient(app)


def test_product_api_crud():
    api = ProductAPI()
    created_status, created = api.handle(
        "POST", "/products", {"name": "Ноутбук", "price": 50000}
    )
    assert created_status == 201
    assert created["id"] == 1

    list_status, listing = api.handle("GET", "/products")
    assert list_status == 200
    assert len(listing["products"]) == 1

    get_status, product = api.handle("GET", "/products/1")
    assert get_status == 200
    assert product["name"] == "Ноутбук"

    put_status, updated = api.handle(
        "PUT", "/products/1", {"name": "Ультрабук", "price": 60000}
    )
    assert put_status == 200
    assert updated["name"] == "Ультрабук"

    missing = api.handle("GET", "/products/9")
    assert missing[0] == 404

    assert api.handle("PATCH", "/products")[0] == 405
    assert api.handle("PATCH", "/products/1")[0] == 405

    delete_status, _ = api.handle("DELETE", "/products/1")
    assert delete_status == 204
    assert api.handle("GET", "/products/1")[0] == 404
    assert api.handle("GET", "/unknown")[0] == 404


def test_product_schemas_and_limiter():
    created = ProductCreate(name="  Мышь  ", price=500, quantity=2, category="Периферия")
    assert created.name == "Мышь"
    with pytest.raises(ValueError):
        ProductCreate(name="   ", price=500, quantity=1, category="ok")
    with pytest.raises(ValueError):
        ProductCreate(name="Мышь", price=500, quantity=1, category="bad!")
    response = ProductResponse.model_validate(
        {"id": 1, "name": "Мышь", "price": 500, "stock": 3}
    )
    assert response.quantity == 3
    assert limiter._key_func is not None


# Правило patch where it is looked up: если бы main.py импортировал имя к себе
# (from ... import create_order), патчили бы 'src.api.main.create_order'.
# В текущем main.py импорта нет, поэтому патчим источник - модуль, где имя объявлено.
@patch("src.services.cache_service.get_cached_products")
def test_get_products(mock_get_cached):
    """Тест получения товаров"""
    mock_get_cached.return_value = [
        {"id": 1, "name": "Ноутбук", "price": 50000, "stock": 5},
        {"id": 2, "name": "Мышь", "price": 500, "stock": 20},
        {"id": 3, "name": "Клавиатура", "price": 1500, "stock": 10},
    ]
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 3
    mock_get_cached.assert_called()


@patch("src.database.queries.create_order")
def test_create_order(mock_create_order):
    """Тест создания заказа"""
    mock_create_order.return_value = 5
    response = client.post(
        "/orders",
        json={"user_id": 1, "product_id": 2, "quantity": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 5
    assert body["message"] == "Заказ создан"
    mock_create_order.assert_called_once_with(
        user_id=1,
        product_id=2,
        quantity=1,
        total=None,
    )
