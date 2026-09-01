import asyncpg


class ProductRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_by_id(self, product_id: int) -> dict | None:
        """Получить товар по id"""
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                "SELECT * FROM products WHERE id = $1", product_id
            )
            return dict(result) if result else None

    async def list_products(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """Список товаров с пагинацией"""
        async with self.pool.acquire() as connection:
            results = await connection.fetch(
                "SELECT * FROM products LIMIT $1 OFFSET $2", limit, offset
            )
            return [dict(result) for result in results]

    async def create(self, name: str, price: float, description: str = "") -> int:
        """Создать товар, вернуть id"""
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                "INSERT INTO products (name, price, description) VALUES ($1, $2, $3) RETURNING id",
                name, price, description
            )
            return result[0] if result else None

    async def update_price(self, product_id: int, new_price: float) -> bool:
        """Обновить цену товара"""
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                "UPDATE products SET price = $1 WHERE id = $2 RETURNING id",
                new_price, product_id
            )
            return bool(result[0]) if result else False

    async def delete(self, product_id: int) -> bool:
        """Удалить товар"""
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                "DELETE FROM products WHERE id = $1 RETURNING id", product_id
            )
            return bool(result[0]) if result else False

