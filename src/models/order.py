from datetime import datetime


class Order:
    """Класс только для хранения данных заказа (SRP)"""

    def __init__(self, user, products, order_id=None, created_at=None):
        self.user = user
        self.products = products
        self.order_id = order_id
        if isinstance(created_at, str):
            self.created_at = datetime.strptime(created_at, "%Y-%m-%d")
        else:
            self.created_at = created_at

    def add_product(self, product):
        if product not in self.products:
            raise KeyError("Товар не найден")
        # Логика добавления товара

    def calculate_total(self):
        """Удобная обёртка для обратной совместимости (делегирует в OrderCalculator)"""
        return OrderCalculator.calculate_total(self)

    def __lt__(self, other):
        """Сравнение по дате (<)"""
        if not isinstance(other, Order):
            return NotImplemented
        return self.created_at < other.created_at

    def __eq__(self, other):
        """Сравнение по ID (==)"""
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id

    def __iter__(self):
        """Итерация по товарам в заказе"""
        return iter(self.products)


class OrderCalculator:
    """Класс для расчетов заказа (SRP)"""

    @staticmethod
    def calculate_total(order: Order) -> float:
        """Рассчитать общую стоимость заказа"""
        total = 0
        for product in order.products:
            total += product.get_total_price()
        return total

    @staticmethod
    def calculate_discount(order: Order, discount_percent: float) -> float:
        """Рассчитать стоимость со скидкой"""
        total = OrderCalculator.calculate_total(order)
        return total * (1 - discount_percent / 100)


class OrderValidator:
    """Класс для валидации заказа (SRP)"""

    @staticmethod
    def validate(order: Order) -> bool:
        """Валидировать заказ"""
        if not order.products:
            raise ValueError("Заказ не может быть пустым")
        if not order.user:
            raise ValueError("Заказ должен иметь пользователя")
        for product in order.products:
            if product.quantity <= 0:
                raise ValueError("Количество товара должно быть положительным")
        return True
