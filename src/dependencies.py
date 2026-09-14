# Файл src/dependencies.py
import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.repositories.product_repository import ProductRepository
from src.services.product_service import ProductService

load_dotenv()

# Те же DB_* из .env, что и в src/database/models.py, но асинхронный драйвер asyncpg
ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER', 'admin')}:{os.getenv('DB_PASSWORD', 'secret')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'sfmshop')}"
)


engine = create_async_engine(ASYNC_DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД с автоматическим закрытием."""
    async with async_session() as session:
        async with session.begin():
            yield session


async def get_product_repository(
    session: AsyncSession = Depends(get_session),
) -> ProductRepository:
    """Репозиторий товаров."""
    return ProductRepository(session)


async def get_order_repository(
    session: AsyncSession = Depends(get_session),
):
    """Репозиторий заказов."""
    from src.repositories.order_repository import OrderRepository

    return OrderRepository(session)


async def get_order_service(
    order_repo=Depends(get_order_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
):
    """Сервис заказов со всеми зависимостями."""
    from src.services.order_service import OrderService

    return OrderService(
        order_repo=order_repo,
        product_repo=product_repo,
    )


async def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductService:
    """Сервис товаров."""
    return ProductService(product_repo=product_repo)
