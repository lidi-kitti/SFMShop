from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import Field

from src.api.auth import TokenUser, get_current_user
from src.dependencies import get_order_repository
from src.repositories.order_repository import OrderRepository
from src.services.async_service import process_orders_async


router = APIRouter(prefix="/orders", tags=["orders"])


def _order_to_dict(order) -> dict:
    return {
        "id": order.id,
        "user_id": order.user_id,
        "total": float(order.total),
        "status": order.status,
    }


@router.get("")
async def list_orders(
    current_user: TokenUser = Depends(get_current_user),
    orders: OrderRepository = Depends(get_order_repository),
):
    """Заказы текущего пользователя."""
    items = await orders.list_all(user_id=current_user.id)
    return [_order_to_dict(order) for order in items]


@router.post("/process", status_code=200)
async def process_orders(
    order_ids: Annotated[list[int], Field(min_length=1)],
    current_user: TokenUser = Depends(get_current_user),
):
    """Параллельная обработка заказов. Ответ после завершения."""
    results = await process_orders_async(order_ids)
    return {
        "status": "success",
        "processed": len(results),
        "results": results,
    }


@router.post("/process-background", status_code=200)
async def process_orders_background(
    order_ids: Annotated[list[int], Field(min_length=1)],
    background_tasks: BackgroundTasks,
    current_user: TokenUser = Depends(get_current_user),
):
    """Принять список заказов и обработать после ответа."""
    background_tasks.add_task(process_orders_async, order_ids)
    return {
        "status": "accepted",
        "message": "Обработка заказов запущена в фоне",
    }
