# Файл scripts/lesson_65_task_queue.py
from collections import deque


class TaskQueueSimulator:
    """Симулятор очереди задач с retry-логикой (как в consumer RabbitMQ)."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.queue: deque = deque()
        self.errors: list[dict] = []
        self.done: list[int] = []

    def publish(self, order_id: int) -> None:
        """Положить задачу в очередь (retry-count = 0)."""
        self.queue.append({"order_id": order_id, "retries": 0})
        print(f"PUBLISH заказ {order_id} (retries=0)")

    def run(self, handler) -> None:
        """Разобрать очередь, вызывая handler(order_id) для каждой задачи."""
        while self.queue:
            task = self.queue.popleft()
            order_id = task["order_id"]
            attempt = task["retries"] + 1
            try:
                handler(order_id)
            except Exception as exc:
                task["retries"] += 1
                if task["retries"] < self.max_retries:
                    print(
                        f"RETRY заказ {order_id}: {exc} "
                        f"(попытка {attempt}/{self.max_retries}) → в конец очереди"
                    )
                    self.queue.append(task)
                else:
                    print(
                        f"DEAD  заказ {order_id}: {exc} "
                        f"(попытка {attempt}/{self.max_retries}) → очередь ошибок"
                    )
                    self.errors.append(task)
            else:
                self.done.append(order_id)
                print(f"OK    заказ {order_id} (попытка {attempt}/{self.max_retries})")


_attempts: dict[int, int] = {}


def handle_order(order_id: int) -> None:
    _attempts[order_id] = _attempts.get(order_id, 0) + 1
    if order_id == 102:
        raise ValueError("нет товара на складе")
    if order_id == 104 and _attempts[order_id] <= 2:
        raise ValueError("таймаут платёжного шлюза")


if __name__ == "__main__":
    sim = TaskQueueSimulator(max_retries=3)
    for oid in [101, 102, 103, 104]:
        sim.publish(oid)
    sim.run(handle_order)

    print("---")
    print(f"Обработано: {sorted(sim.done)}")
    print(f"В очереди ошибок: {[t['order_id'] for t in sim.errors]}")