import asyncio
import random


async def order_producer(queue: asyncio.Queue, num_orders: int):
    """Генерация заказов"""
    # Твой код здесь
    for i in range(num_orders):
        order = f"Order {i+1}"
        await queue.put(order)
        print(f"Producer produced {order}")
        await asyncio.sleep(random.uniform(0.1, 0.5))
    await queue.put(None)
    print(f"Producer finished")


async def order_worker(name: str, queue: asyncio.Queue):
    """Обработка заказов из очереди"""
    # Твой код здесь
    while True:
        order = await queue.get()
        if order is None:
            break
        print(f"Worker {name} processed {order}")
        await asyncio.sleep(random.uniform(0.1, 0.5))
        queue.task_done()
    print(f"Worker {name} finished")


async def main():
    queue = asyncio.Queue(maxsize=5)
    num_workers = 3
    num_orders = 10
    # Твой код здесь
    producers = [order_producer(queue, num_orders) for i in range(num_workers)]
    workers = [order_worker(f"Worker {i+1}", queue) for i in range(num_workers)]
    await asyncio.gather(*producers, *workers)
    print("All orders processed")

asyncio.run(main())