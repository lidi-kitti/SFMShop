from abc import ABC, abstractmethod
from src.models.order import Order
from src.services.order_validator import OrderValidator
from src.services.order_calculator import OrderCalculator, DiscountStrategy

class NotificationService(ABC):
    @abstractmethod
    def send(self, order: Order):
        pass

class Database(ABC):
    @abstractmethod
    def save(self, order: Order):
        pass
class OrderService:
    """Сервис для обработки заказов (DIP)"""
    def __init__(self, notification_service: NotificationService, database: Database):
        self.notification_service = notification_service
        self.database = database
    
    def process_order(self, order: Order, discount: DiscountStrategy = None):
        """Обработка заказа"""
        OrderValidator.validate(order)
        total = OrderCalculator.calculate_total(order)
        if discount:
            total = OrderCalculator.apply_discount(order, discount)
        self.notification_service.send(order)
        self.database.save(order)
        return total