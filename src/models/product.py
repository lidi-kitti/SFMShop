from exceptions import ValidationError
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    quantity: int

    def __post_init__(self):
        """Валидация после инициализации"""
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if self.quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
   
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

# Тестирование
try:
    product = Product("Ноутбук", -1000, 10) # Ошибка при создании
except ValueError as e:
    print(f"Ошибка: {e}")

product = Product("Ноутбук", 1000, 10)
print(product.price) # 1000