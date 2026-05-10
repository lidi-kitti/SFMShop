from models.exceptions import ValidationError

class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f"Товар: {self.name}, Цена: {self.price} руб., Количество: {self.quantity}"

    def __repr__(self):
        return f"Product('{self.name}', {self.price}, {self.quantity})"

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