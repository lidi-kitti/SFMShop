from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.models.product import Product
from src.models.user import User
from src.services.discounts import DiscountStrategy, FixedDiscount, PercentDiscount
from src.services.exchange_client import ExchangeClient
from src.services.order_calculator import OrderCalculator
from src.services.order_validator import OrderValidator
from src.services.product_calculator import ProductCalculator
from src.services.product_validator import ProductValidator


@pytest.fixture
def valid_product():
    return Product("Мышь", 500, 3)


def test_percent_and_fixed_discount():
    assert PercentDiscount(10).apply(1000) == 900
    assert FixedDiscount(200).apply(150) == 0
    assert FixedDiscount(50).apply(200) == 150


def test_product_validator_ok(valid_product):
    assert ProductValidator.validate(valid_product) is True


def test_product_validator_errors():
    with pytest.raises(ValueError, match="название"):
        ProductValidator.validate(Product("", 100, 1))
    with pytest.raises(ValueError, match="Цена"):
        ProductValidator.validate(Product("Мышь", 0, 1))


def test_product_calculator(valid_product):
    assert ProductCalculator.calculate_total_value(valid_product) == 1500
    assert ProductCalculator.apply_discount(valid_product, PercentDiscount(10)) == 450


def test_service_order_calculator_and_validator():
    user = User("Анна", "anna@sfmshop.ru")
    items = [SimpleNamespace(price=1000, quantity=2)]
    order = SimpleNamespace(items=items, user=user)
    assert OrderCalculator.calculate_total(order) == 2000
    assert OrderCalculator.apply_discount(order, PercentDiscount(10)) == 1800
    assert OrderValidator.validate(order) is True
    with pytest.raises(ValueError, match="пустым"):
        OrderValidator.validate(SimpleNamespace(items=[], user=user))
    with pytest.raises(ValueError, match="пользователя"):
        OrderValidator.validate(SimpleNamespace(items=items, user=None))


def test_discount_strategy_is_abstract():
    assert issubclass(PercentDiscount, DiscountStrategy)


@patch("src.services.exchange_client.requests.get")
def test_get_exchange_rate(mock_get):
    """Тест: курс берётся из ответа внешнего API, сети нет"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"rates": {"RUB": 92.5, "EUR": 0.91}}
    mock_get.return_value = mock_response

    client = ExchangeClient()
    rate = client.get_exchange_rate("USD", "RUB")

    assert rate == 92.5
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0].endswith("/USD")
    assert kwargs["timeout"] == client.timeout


@patch("src.services.exchange_client.requests.get")
def test_get_exchange_rate_currency_missing(mock_get):
    """Тест: нужной валюты нет в ответе API"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"rates": {"EUR": 0.91}}
    mock_get.return_value = mock_response

    client = ExchangeClient()
    assert client.get_exchange_rate("USD", "RUB") is None
    mock_get.assert_called_once()

