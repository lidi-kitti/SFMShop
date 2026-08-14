# Файл src/services/product_validator.py
from src.models.product import Product

class ProductValidator:
    """Класс для валидации товара (SRP)"""
    @staticmethod
    def validate(product: Product) -> bool:
        """Валидировать товар"""
        if not product.name:
            raise ValueError("Товар должен иметь название")
        if product.price <= 0:
            raise ValueError("Цена должна быть положительной")
        if product.quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        return True