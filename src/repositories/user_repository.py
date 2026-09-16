from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.models import Order, OrderItem, User


class UserRepository:
    """Репозиторий пользователей для цепочки Depends."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(User))
        return list(result.scalars().all())

    async def get_orders(self, user_id: int) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .where(Order.user_id == user_id)
        )
        return list(result.unique().scalars().all())
