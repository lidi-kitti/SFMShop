from abc import ABC, abstractmethod
from src.models.order import Order

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price: float) -> float:
        pass

class PercentDiscount(DiscountStrategy):
    def __init__(self, percent: float):
        self.percent = percent
    
    def apply(self, price: float) -> float:
        return price * (1 - self.percent / 100)

class OrderCalculator:
    """Класс для расчетов заказа (SRP)"""
    @staticmethod
    def calculate_total(order: Order) -> float:
        total = 0
        for item in order.items:
            total += item.price * item.quantity
        return total
    
    @staticmethod
    def apply_discount(order: Order, discount: DiscountStrategy) -> float:
        total = OrderCalculator.calculate_total(order)
        return discount.apply(total)