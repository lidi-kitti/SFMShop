# tests/test_utils.py
from types import SimpleNamespace

import pytest

from src.utils.calculations import (
    benchmark_calculate_total,
    benchmark_search,
    calculate_discount,
    calculate_total,
    calculate_total_orders,
    calculate_total_orders_slow,
    create_products_index,
    find_product_in_dict,
    find_product_in_list,
)
from src.utils.validators import validate_age, validate_email


@pytest.mark.parametrize(
    "price, discount_rate, expected",
    [
        (1000, 0.1, 100),
        (500, 0.2, 100),
        (2500, 0, 0),
        (200, 1, 200),
    ],
)
def test_calculate_discount(price, discount_rate, expected):
    assert calculate_discount(price, discount_rate) == expected


@pytest.mark.parametrize(
    "price, quantity, expected",
    [
        (1000, 2, 2000),
        (500, 1, 500),
        (250, 0, 0),
        (99.5, 4, 398.0),
    ],
)
def test_calculate_total(price, quantity, expected):
    assert calculate_total(price, quantity) == expected


@pytest.mark.parametrize("age, expected", [(17, False), (18, True), (30, True)])
def test_validate_age(age, expected):
    assert validate_age(age) is expected


@pytest.mark.parametrize(
    "email, expected",
    [
        ("anna@sfmshop.ru", True),
        ("bad", False),
        ("no-dot@local", False),
    ],
)
def test_validate_email(email, expected):
    assert validate_email(email) is expected


def test_order_totals_and_benchmark():
    item = SimpleNamespace(price=1000, quantity=2)
    orders = [
        SimpleNamespace(items=[item], total=2000),
        SimpleNamespace(items=[SimpleNamespace(price=500, quantity=1)], total=500),
    ]
    assert calculate_total_orders_slow(orders) == 2500
    assert calculate_total_orders(orders) == 2500
    report = benchmark_calculate_total(orders)
    assert report["result"] == 2500
    assert report["speedup"] >= 0


def test_product_search_and_benchmark():
    products = [
        SimpleNamespace(id=1, name="Ноутбук"),
        SimpleNamespace(id=2, name="Мышь"),
    ]
    assert find_product_in_list(products, 2).name == "Мышь"
    assert find_product_in_list(products, 99) is None
    index = create_products_index(products)
    assert find_product_in_dict(index, 1).name == "Ноутбук"
    assert find_product_in_dict(index, 99) is None
    report = benchmark_search(products, 2)
    assert report["result"].id == 2
