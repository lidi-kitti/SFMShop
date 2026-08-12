from datetime import datetime

class Order:
    def __init__(self, user, products, order_id, created_at, total):
        self.user = user
        self.products = products
        self.order_id = order_id
        self.created_at = datetime.strptime(created_at, "%Y-%m-%d")
        self.total = total
        self.status = "pending"

    def __lt__(self, other):
        return self.created_at < other.created_at

    def __eq__(self, other):
        return self.created_at == other.created_at

    def add_product(self, product):
        self.products.append(product)

    def calculate_total(self):
        total = 0
        for product in self.products:
            total = total + product.price * product.quantity
        return total

    def __str__(self):
        return f"Заказ пользователя {self.user.name} на сумму {self.calculate_total()} руб."