from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    """Абстрактный класс для стратегий скидок (OCP)"""

    @abstractmethod
    def apply(self, price: float) -> float:
        """Применить скидку к цене"""
        pass


class PercentDiscount(DiscountStrategy):
    """Скидка в процентах"""

    def __init__(self, percent: float):
        self.percent = percent

    def apply(self, price: float) -> float:
        return price * (1 - self.percent / 100)


class FixedDiscount(DiscountStrategy):
    """Фиксированная скидка"""

    def __init__(self, amount: float):
        self.amount = amount

    def apply(self, price: float) -> float:
        return max(0, price - self.amount)


class Product:
    """Доменная модель товара SFMShop (канон ba7, урок 40 «Рефакторинг»).

    После рефакторинга класс хранит данные товара и умеет считать
    стоимость партии и цену со скидкой через стратегию (OCP).
    Валидация цены и количества — прямо в конструкторе
    (price < 0 / quantity < 0 -> ValueError). Магические методы
    __str__/__repr__/__lt__/__eq__ накоплены с урока 17 «Магические
    методы» и сохранены при рефакторинге.
    """

    def __init__(self, name, price, quantity=0):
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        self.name = name
        self.price = price
        self.quantity = quantity

    def get_total_price(self):
        """Общая стоимость партии товара (из урока 15)"""
        return self.price * self.quantity

    def calculate_price(self, discount: DiscountStrategy = None) -> float:
        """Расчет цены со скидкой - открыт для расширения (OCP)"""
        if discount is None:
            return self.price
        return discount.apply(self.price)

    def to_json(self):
        return {"name": self.name, "price": self.price, "quantity": self.quantity}

    def __str__(self):
        return f"{self.name}: {self.price} руб. (в наличии: {self.quantity})"

    def __repr__(self):
        return f"Product(name={self.name!r}, price={self.price}, quantity={self.quantity})"

    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return (self.name, self.price, self.quantity) == (
            other.name,
            other.price,
            other.quantity,
        )

    def __lt__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price
