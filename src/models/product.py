from exceptions import ValidationError
from dataclasses import dataclass
from metaclasses import ModelMeta
from descriptors import PositiveNumber, CachedProperty

class Product(metaclass=ModelMeta):
    price = PositiveNumber("price")
    quantity = PositiveNumber("quantity")

    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __lt__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price

    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        return self.name == other.name and self.price == other.price

#Функция для обновления цены
    def set_price(self, price):
        if price<0:
            raise ValidationError("Цена не может быть отрицательной")
        self.price = price

    @CachedProperty
    def total_value(self):
        print(f"Вычисление total_value для {self.name}")
        return self.price * self.quantity
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["price"], data["quantity"])

    @staticmethod
    def calculate_discount(price, discount_percent):
        return price * (1 - discount_percent / 100)

    
# Тестирование
product = Product("Ноутбук", 1000, 10)

# Первое обращение - вычисление
print(product.total_value)  # Вычисление... 10000

# Второе обращение - из кэша
print(product.total_value)  # 10000 (без вычисления)