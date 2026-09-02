import asyncio
import time

import aiohttp
from sqlalchemy import select

from src.database.models import Order, get_session


async def fetch_order_details_async(order_id: int):
    """Получить дополнительные данные о заказе из внешнего API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.example.com/order/{order_id}") as response:
                if response.status == 200:
                    return await response.json()
                return None
    except Exception as e:
        print(f"Ошибка при запросе данных для заказа {order_id}: {e}")
        return None


def _mark_order_processed(order_id: int):
    db = get_session()
    try:
        order = db.execute(select(Order).where(Order.id == order_id)).scalar_one_or_none()
        if not order:
            raise ValueError(f"Заказ {order_id} не найден")
        order.status = "processed"
        db.commit()
        return f"Заказ {order_id} обработан"
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def process_order(order_id: int):
    """Асинхронная обработка одного заказа"""
    try:
        await asyncio.sleep(0.1)
        return await asyncio.to_thread(_mark_order_processed, order_id)
    except Exception as e:
        return f"Ошибка при обработке заказа {order_id}: {e}"


async def process_orders_sync(order_ids: list):
    """Последовательная обработка списка заказов"""
    results = []
    for order_id in order_ids:
        results.append(await process_order(order_id))
    return results


async def process_orders_async(order_ids: list):
    """Параллельная обработка списка заказов"""
    tasks = [process_order(order_id) for order_id in order_ids]
    return await asyncio.gather(*tasks)


async def main():
    order_ids = list(range(1, 101))

    start = time.time()
    await process_orders_async(order_ids)
    end = time.time()
    print(f"Асинхронная обработка: {end - start} секунд")

    start = time.time()
    await process_orders_sync(order_ids)
    end = time.time()
    print(f"Синхронная обработка: {end - start} секунд")


if __name__ == "__main__":
    asyncio.run(main())
