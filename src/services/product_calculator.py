from src.services.discounts import DiscountStrategy  # класс из Шага 3
from src.models.product import Product

class ProductCalculator:
    """Класс для расчетов товара (SRP)"""
    @staticmethod
    def calculate_total_value(product: Product) -> float:
        """Рассчитать общую стоимость товара"""
        return product.price * product.quantity

    @staticmethod
    def apply_discount(product: Product, discount: DiscountStrategy) -> float:
        """Применить скидку к цене товара"""
        return discount.apply(product.price)