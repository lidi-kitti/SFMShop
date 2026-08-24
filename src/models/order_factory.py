from models.order import Order, OrderValidator

class OrderFactory:
    """Фабрика для создания заказов"""
    @staticmethod
    def create_order(order_id, items, user):
        order = Order(user, items, order_id=order_id)
        OrderValidator.validate(order)
        return order
    
    @classmethod
    def create_order_from_dict(cls, data):
        """Создание заказа из словаря"""
        return cls.create_order(
            data["order_id"],
            data["items"],
            data["user"]
        )