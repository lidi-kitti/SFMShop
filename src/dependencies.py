# Файл src/dependencies.py
import os
from collections.abc import AsyncGenerator
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.api.auth import decode_access_token
from src.database.models import User
from src.repositories.order_repository import OrderRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.user_repository import UserRepository
from src.services.cache_service import CacheService
from src.services.product_service import ProductService

load_dotenv()

# Те же DB_* из .env, что и в src/database/models.py, но асинхронный драйвер asyncpg
ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER', 'admin')}:{os.getenv('DB_PASSWORD', 'secret')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'sfmshop')}"
)


engine = create_async_engine(ASYNC_DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
bearer_scheme = HTTPBearer(auto_error=False)
cache_service = CacheService()


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


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    """Репозиторий пользователей."""
    return UserRepository(session)


async def get_order_repository(
    session: AsyncSession = Depends(get_session),
) -> OrderRepository:
    """Репозиторий заказов."""
    return OrderRepository(session)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Текущий пользователь: Bearer-сессия Redis → строка users."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Требуется заголовок Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id") if payload else None
    if user_id is None:
        session_data = cache_service.get_user_session(token)
        if not session_data:
            raise HTTPException(
                status_code=401,
                detail="Сессия недействительна или истекла",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = session_data.get("user_id")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Пользователь сессии не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
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
