from exceptions import ValidationError
from dataclasses import dataclass
from metaclasses import ModelMeta
from descriptors import PositiveNumber

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

    def apply_discount(self, price):
        pass

    def check_stock(self):
        pass

    def update_stock(self):
        pass

    def get_total_price(self):
        #другой комментарий
        pass
    def calculate_shipping(self):
        pass
    def get_category(self):
        pass
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["price"], data["quantity"])

    @staticmethod
    def calculate_discount(price, discount_percent):
        return price * (1 - discount_percent / 100)

    

# Тестирование
product = Product("Ноутбук", 1000, 10)
print(product.price) # 1000

try:
    product.price = -100 # Ошибка: ValueError
except ValueError as e:
    print(f"Ошибка: {e}")

try:
    product.quantity = -5 # Ошибка: ValueError
except ValueError as e:
    print(f"Ошибка: {e}")
