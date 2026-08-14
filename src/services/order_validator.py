from src.models.order import Order
class OrderValidator:
    """Класс для валидации заказа (SRP)"""
    @staticmethod
    def validate(order: Order) -> bool:
        if not order.items:
            raise ValueError("Заказ не может быть пустым")
        if not order.user:
            raise ValueError("Заказ должен иметь пользователя")
        return True