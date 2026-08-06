# Файл src/models/delivery.py
from abc import ABC, abstractmethod

class Delivery(ABC):
    """Абстрактный класс для доставки"""
    def __init__(self, order):
        self.order = order

    @abstractmethod
    def calculate_cost(self):
        """Расчет стоимости доставки"""
        pass

class StandartDelivery(Delivery):
    """Стандартная доставка"""
    def __init__(self, order):
        self.order = order

    def calculate_cost(self):
        """Расчет стоимости доставки"""
        return 100


class ExpressDelivery(Delivery):
    """Экспресс доставка"""
    def __init__(self, order):
        self.order = order

    def calculate_cost(self):
        """Расчет стоимости доставки"""
        return 200


class PickupDelivery(Delivery):
    """Самовывоз"""
    def __init__(self, order):
        self.order = order

    def calculate_cost(self):