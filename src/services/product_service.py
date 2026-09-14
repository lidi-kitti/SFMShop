# Файл src/services/product_service.py
from src.database.models import Product
from src.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def get_product(self, product_id: int) -> Product:
        """Получить товар или бросить ошибку."""
        product = await self.product_repo.get_by_id(product_id)
        if product is None:
            raise ValueError(f"Товар {product_id} не найден")
        return product

    async def search_products(
        self,
        name_query: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        ) -> list[Product]:
        """Поиск товаров с фильтрами."""
        return await self.product_repo.search(
            name_query=name_query,
            min_price=min_price,
            max_price=max_price,
            )