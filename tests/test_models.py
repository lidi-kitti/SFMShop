# tests/test_models.py
import pytest
from src.models.product import (
    Product,
    PercentDiscount,
    FixedDiscount,
    calculate_order_total,
    calculate_order_total_original,
)
from src.models.user import User
from src.models.order import Order, OrderCalculator, OrderValidator


@pytest.fixture
def sample_product():
    """Фикстура: тестовый товар"""
    return Product("Ноутбук", 1000, 2)


@pytest.fixture
def sample_user():
    """Фикстура: тестовый пользователь"""
    return User("Анна", "anna@sfmshop.ru")


@pytest.fixture
def sample_order(sample_user, sample_product):
    """Фикстура: заказ с ноутбуком и мышью"""
    mouse = Product("Мышь", 500, 1)
    return Order(sample_user, [sample_product, mouse], order_id=101)


def test_create_product(sample_product):
    assert sample_product.name == "Ноутбук"
    assert sample_product.price == 1000
    assert sample_product.quantity == 2


def test_product_validation_negative_price():
    with pytest.raises(ValueError):
        Product("Брак", -1, 1)


def test_product_validation_negative_quantity():
    with pytest.raises(ValueError):
        Product("Брак", 100, -5)


def test_product_methods(sample_product):
    assert sample_product.get_total_price() == 2000
    assert sample_product.calculate_price() == 1000
    assert sample_product.calculate_price(PercentDiscount(10)) == 900
    assert sample_product.calculate_price(FixedDiscount(200)) == 800
    assert sample_product.to_json() == {
        "name": "Ноутбук",
        "price": 1000,
        "quantity": 2,
    }
    assert "Ноутбук" in str(sample_product)
    assert "Product" in repr(sample_product)
    assert sample_product.to_dict()["name"] == "Ноутбук"
    assert sample_product.total_price == 2000
    assert sample_product.total_price == 2000


def test_product_eq_and_lt(sample_product):
    same = Product("Ноутбук", 1000, 2)
    cheaper = Product("Мышь", 500, 1)
    assert sample_product == same
    assert cheaper < sample_product
    assert sample_product.__eq__("нет") is NotImplemented
    assert sample_product.__lt__("нет") is NotImplemented


def test_create_user(sample_user):
    assert sample_user.name == "Анна"
    assert sample_user.email == "anna@sfmshop.ru"
    assert sample_user.get_info() == "Пользователь: Анна, Email: anna@sfmshop.ru"


def test_user_validation_no_at():
    with pytest.raises(ValueError):
        User("Иван", "ivan-sfmshop.ru")


def test_user_validation_no_dot():
    with pytest.raises(ValueError):
        User("Иван", "ivan@sfmshop")


def test_user_age(sample_user):
    sample_user.age = 25
    assert sample_user.age == 25
    with pytest.raises(ValueError):
        sample_user.age = 200


def test_create_order(sample_order, sample_user, sample_product):
    """Тест: создание заказа"""
    assert sample_order.order_id == 101
    assert sample_order.user is sample_user
    assert sample_order.user.name == "Анна"
    assert sample_order.products[0] is sample_product
    assert len(sample_order.products) == 2
    assert len(sample_order) == 2


def test_calculate_total(sample_order):
    """Тест: расчет стоимости заказа"""
    assert sample_order.calculate_total() == 1000 * 2 + 500 * 1
    assert sample_order.calculate_total() == 2500


def test_order_created_at_from_string(sample_user, sample_product):
    order = Order(sample_user, [sample_product], order_id=7, created_at="2026-01-15")
    assert order.created_at.year == 2026
    assert order.created_at.month == 1
    assert order.created_at.day == 15


def test_order_add_product(sample_order, sample_product):
    sample_order.add_product(sample_product)
    with pytest.raises(KeyError):
        sample_order.add_product(Product("Клавиатура", 300, 1))


def test_order_magic(sample_order, sample_user):
    other = Order(sample_user, [Product("Клавиатура", 300, 1)], order_id=50)
    assert "Ноутбук" in sample_order
    assert sample_order.products[0] in sample_order
    assert sample_order[0].name == "Ноутбук"
    assert list(sample_order)[1].name == "Мышь"
    merged = sample_order + other
    assert len(merged.products) == 3
    assert sample_order == Order(sample_user, [], order_id=101)
    assert sample_order != "нет"
    assert other < sample_order
    dated = Order(sample_user, [], order_id=1, created_at="2020-01-01")
    later = Order(sample_user, [], order_id=2, created_at="2021-01-01")
    assert dated < later
    assert sample_order.__lt__("нет") is NotImplemented
    assert sample_order.__add__("нет") is NotImplemented


def test_order_calculator_discount(sample_order):
    assert OrderCalculator.calculate_discount(sample_order, 20) == 2000


def test_order_validator(sample_order, sample_user):
    assert OrderValidator.validate(sample_order) is True
    with pytest.raises(ValueError, match="пустым"):
        OrderValidator.validate(Order(sample_user, [], order_id=1))
    with pytest.raises(ValueError, match="пользователя"):
        OrderValidator.validate(Order(None, [Product("Мышь", 500, 1)], order_id=2))
    with pytest.raises(ValueError, match="Количество"):
        OrderValidator.validate(
            Order(sample_user, [Product("Мышь", 500, 0)], order_id=3)
        )


def test_dict_order_totals():
    payload = {
        "id": 1,
        "items": [
            {"name": "Ноутбук", "price": 1000, "quantity": 2},
            {"name": "Мышь", "price": 500, "quantity": 1},
        ],
    }
    assert calculate_order_total_original(payload) == 2500
    assert calculate_order_total(payload) == 2500
    assert calculate_order_total({}) == 0
    assert calculate_order_total({"items": None}) == 0


def test_cart_delivery_notifications_and_mixins():
    from src.models.cart import ShoppingCart
    from src.models.delivery import ExpressDelivery, StandardDelivery, process_delivery
    from src.models.delivery_stragedy import (
        ExpressDelivery as ExpressStrategy,
        StandardDelivery as StandardStrategy,
    )
    from src.models.exceptions import (
        InsufficientStockError,
        InvalidOrderError,
        NegativePriceError,
        SFMShopException,
    )
    from src.models.mixins import LoggableMixin, SerializableMixin, ValidatableMixin
    from src.models.notifications import EmailNotification, SMSNotification
    from src.models.order_factory import OrderFactory

    cart = ShoppingCart() + "ноутбук"
    assert len(cart) == 1
    assert list(cart) == ["ноутбук"]
    assert "1" in str(cart)

    assert process_delivery(StandardDelivery(), 3) == 30
    assert process_delivery(ExpressDelivery(), 3) == 60
    assert StandardStrategy().calculate_cost(2) == 20
    assert ExpressStrategy().calculate_cost(2) == 40

    EmailNotification("a@b.c").send()
    SMSNotification("123").send("ок")

    assert issubclass(InsufficientStockError, SFMShopException)
    assert issubclass(InvalidOrderError, SFMShopException)
    assert issubclass(NegativePriceError, Exception)

    class Dummy(ValidatableMixin, LoggableMixin, SerializableMixin):
        def validate(self):
            raise ValueError("нет")

    dummy = Dummy()
    dummy.log("тест")
    assert dummy.is_valid() is False
    assert dummy.to_json()["class"] == "Dummy"
    assert ValidatableMixin().is_valid() is True

    user = User("Анна", "anna@sfmshop.ru")
    laptop = Product("Ноутбук", 1000, 2)
    factory_order = OrderFactory.create_order(9, [laptop], user)
    assert factory_order.order_id == 9
    from_dict = OrderFactory.create_order_from_dict(
        {"order_id": 10, "items": [laptop], "user": user}
    )
    assert from_dict.order_id == 10


def test_payment_and_config():
    from src.core.config import settings
    from src.models import payment as payment_module

    assert isinstance(settings.anthropic_api_key, str)
    assert payment_module.CardPayment(50).process() is True
    assert payment_module.CardPayment(50).to_json()["amount"] == 50
