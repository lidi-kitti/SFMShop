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
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["price"], data["quantity"])

    @staticmethod
    def calculate_discount(price, discount_percent):
        return price * (1 - discount_percent / 100)


# Тестирование
raw_products = [
    {"name": "Ноутбук", "price": 1000, "quantity": 10},
    {"name": "Мышь", "price": 500, "quantity": 20},
    {"name": "Клавиатура", "price": 800, "quantity": 5},
]
products = [Product.from_dict(product) for product in raw_products]
for product in products:
    print(product)
    print(product.calculate_discount(product.price, 25)) 
