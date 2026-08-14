from abc import ABC, abstractmethod


class Delivery(ABC):
    """Абстрактный класс для доставки"""

    @abstractmethod
    def calculate_cost(self, distance: float) -> float:
        """Рассчитать стоимость доставки"""
        pass


class StandardDelivery(Delivery):
    """Стандартная доставка"""

    def calculate_cost(self, distance: float) -> float:
        """Стоимость = расстояние * 10"""
        return distance * 10


class ExpressDelivery(Delivery):
    """Экспресс-доставка"""

    def calculate_cost(self, distance: float) -> float:
        """Стоимость = расстояние * 20"""
        return distance * 20


def process_delivery(delivery: Delivery, distance: float) -> float:
    """Обработать доставку - работает с любым типом Delivery (полиморфизм)"""
    return delivery.calculate_cost(distance)
