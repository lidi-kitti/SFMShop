from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Order


class OrderRepository:
    """Репозиторий заказов для цепочки Depends."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: int) -> Order | None:
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def list_all(self, user_id: int | None = None) -> list[Order]:
        query = select(Order).order_by(Order.order_date.desc())
        if user_id is not None:
            query = query.where(Order.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.flush()
        return order
