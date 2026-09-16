from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import TokenUser, get_current_user
from src.database.models import User
from src.dependencies import get_session, get_user_repository
from src.repositories.user_repository import UserRepository


router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)


def _user_to_dict(user: User) -> dict:
    return {"id": user.id, "name": user.name, "email": user.email}


def _order_to_dict(order) -> dict:
    return {
        "id": order.id,
        "user_id": order.user_id,
        "total": float(order.total),
        "status": order.status,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else None,
                "quantity": item.quantity,
                "price": float(item.price),
            }
            for item in order.items
        ],
    }


@router.get("")
async def list_users(
    current_user: TokenUser = Depends(get_current_user),
    users: UserRepository = Depends(get_user_repository),
):
    """Список пользователей. Нужен JWT в Authorization."""
    items = await users.get_all()
    return [_user_to_dict(user) for user in items]


@router.get("/me")
async def read_me(current_user: TokenUser = Depends(get_current_user)):
    """Текущий пользователь из JWT (Depends(get_current_user))."""
    return {"id": current_user.id, "username": current_user.username}


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: TokenUser = Depends(get_current_user),
    users: UserRepository = Depends(get_user_repository),
):
    user = await users.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return _user_to_dict(user)


@router.get("/{user_id}/orders")
async def get_user_orders(
    user_id: int,
    current_user: TokenUser = Depends(get_current_user),
    users: UserRepository = Depends(get_user_repository),
):
    user = await users.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    orders = await users.get_orders(user_id)
    return {
        "user_id": user.id,
        "user_name": user.name,
        "orders": [_order_to_dict(order) for order in orders],
    }


@router.post("", status_code=201)
async def create_user(body: UserCreate, session: AsyncSession = Depends(get_session)):
    """Регистрация без Bearer."""
    user = User(name=body.name, email=body.email)
    session.add(user)
    try:
        await session.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
    return {**_user_to_dict(user), "balance": float(user.balance)}
