# Файл scripts/lesson_64_message_broker.py
from queue import Queue


class MessageBroker:
    """Брокер сообщений в памяти для SFMShop: очередь задач + retry + dead-letter."""

    def __init__(self, max_retries=3):
        self.queue = Queue()
        self.dead_letter = []
        self.max_retries = max_retries

    def publish(self, task):
        # Producer: положить задачу в очередь
        self.queue.put(task)

    def consume(self, handlers):
        # Consumer: обработать все задачи, повторяя упавшие и отправляя
        # окончательно упавшие в dead-letter
        while not self.queue.empty():
            task = self.queue.get()
            name = task["task"]
            handler = handlers[name]
            ok = handler(task)
            if ok:
                print(f"OK {name} order={task['order_id']} attempt={task['attempts'] + 1}")
            else:
                task["attempts"] += 1
                if task["attempts"] < self.max_retries:
                    print(f"RETRY {name} order={task['order_id']} attempt={task['attempts']}")
                    self.queue.put(task)
                else:
                    print(f"DEAD {name} order={task['order_id']} attempts={task['attempts']}")
                    self.dead_letter.append(task)
            self.queue.task_done()


def main():
    broker = MessageBroker(max_retries=3)
    broker.publish({"task": "send_email", "order_id": 101, "attempts": 0})
    broker.publish({"task": "update_stock", "order_id": 101, "attempts": 0})
    broker.publish({"task": "generate_report", "order_id": 101, "attempts": 0})

    handlers = {
        "send_email": lambda task: True,
        "update_stock": lambda task: task["attempts"] >= 2,  # пройдёт с 3-й попытки
        "generate_report": lambda task: False,               # всегда падает
    }
    broker.consume(handlers)

    print(f"Dead-letter: {len(broker.dead_letter)}")
    for task in broker.dead_letter:
        print(f"  {task['task']} order={task['order_id']}")


if __name__ == "__main__":
    main()