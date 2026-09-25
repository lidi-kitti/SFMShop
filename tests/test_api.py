import pytest

from src.api.limiter import limiter
from src.api.router import ProductAPI
from src.api.schemas import ProductCreate
from src.schemas.product import ProductResponse


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
