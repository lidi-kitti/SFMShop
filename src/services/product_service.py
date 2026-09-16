# Файл src/services/product_service.py
from src.database.models import Product
from src.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def create_product(self, name: str, price, stock: int) -> Product:
        """Создать товар в каталоге."""
        product = Product(name=name, price=price, stock=stock)
        return await self.product_repo.create(product)


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