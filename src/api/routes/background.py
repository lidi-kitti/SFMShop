# Файл src/api/routes/background.py
import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database.models import Order, Product, get_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["background"])


def get_db():
    db = get_session()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def send_confirmation_email(order_id: int, email: str):
    """Фоновая отправка письма. SMTP в проекте нет — только лог."""
    logger.info("Письмо о подтверждении заказа %s → %s", order_id, email)
    print(f"Email отправлен: заказ {order_id} → {email}")


@router.post("/orders/{order_id}/confirm")
async def confirm_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    """Сразу подтвердить заказ; письмо уйдёт после ответа."""
    order = db.execute(
        select(Order).options(joinedload(Order.user)).where(Order.id == order_id)
    ).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    order.status = "confirmed"
    db.commit()

    email = order.user.email if order.user else "unknown@sfmshop.local"
    background_tasks.add_task(send_confirmation_email, order_id, email)

    return {
        "order_id": order.id,
        "status": "confirmed",
        "message": "Заказ подтверждён, письмо отправляется в фоне",
    }


# Файл src/api/routes/background.py (дополнение)
# router уже объявлен в этом файле в задании 1, второй раз не нужен
task_statuses: dict[str, dict] = {}


def export_catalog(task_id: str):
    """Выгрузить каталог товаров и обновить прогресс в task_statuses."""
    task_statuses[task_id] = {"status": "running", "progress": 0}
    db = get_session(read_only=True)
    try:
        products = db.execute(select(Product)).scalars().all()
        exported = []
        total = len(products)
        for index, product in enumerate(products, start=1):
            exported.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "price": float(product.price),
                    "stock": product.stock,
                }
            )
            task_statuses[task_id] = {
                "status": "running",
                "progress": int(index / total * 100) if total else 100,
                "exported": index,
            }
        task_statuses[task_id] = {
            "status": "completed",
            "progress": 100,
            "count": len(exported),
            "products": exported,
        }
        logger.info("Экспорт %s завершён: %s товаров", task_id, len(exported))
    except Exception as exc:
        logger.exception("Экспорт %s упал: %s", task_id, exc)
        task_statuses[task_id] = {"status": "failed", "error": str(exc)}
    finally:
        db.close()


@router.post("/exports")
async def start_export(background_tasks: BackgroundTasks):
    """Запустить фоновый экспорт каталога и сразу вернуть task_id."""
    task_id = str(uuid.uuid4())
    task_statuses[task_id] = {"status": "pending", "progress": 0}
    background_tasks.add_task(export_catalog, task_id)
    return {"task_id": task_id, "status": "accepted"}


@router.get("/exports/{task_id}")
async def get_export_status(task_id: str):
    """Статус фонового экспорта по task_id."""
    task = task_statuses.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача экспорта не найдена")
    return {"task_id": task_id, **task}


# Файл src/api/routes/background.py (дополнение)
# router уже объявлен в этом файле в задании 1, второй раз не нужен


class BackgroundOrderCreate(BaseModel):
    user_email: str
    items: list[dict]
    total: float


def send_email(order_id: int, email: str):
    logger.info("Фон: email заказа %s → %s", order_id, email)
    print(f"Email отправлен: заказ {order_id} → {email}")


def update_stock(order_id: int, items: list[dict]):
    logger.info("Фон: склад заказа %s, items=%s", order_id, items)
    print(f"Остатки обновлены: заказ {order_id}, позиций {len(items)}")


def notify_manager(order_id: int, total: float):
    logger.info("Фон: менеджер, заказ %s, сумма %s", order_id, total)
    print(f"Менеджер уведомлён: заказ {order_id}, сумма {total}")


@router.post("/orders/background")
async def create_order(order: BackgroundOrderCreate, background_tasks: BackgroundTasks):
    """Сразу ответить; email, склад и менеджер — после ответа, по очереди."""
    order_id = 42
    background_tasks.add_task(send_email, order_id, order.user_email)
    background_tasks.add_task(update_stock, order_id, order.items)
    background_tasks.add_task(notify_manager, order_id, order.total)
    return {"order_id": order_id, "status": "processing"}
