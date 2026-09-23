# Файл src/services/queue_producer.py
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Union

import pika

_project_root = Path(__file__).resolve().parents[2]
_models_dir = _project_root / "src" / "models"
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
# src.models.order импортирует metaclasses без пакета src
if str(_models_dir) not in sys.path:
    sys.path.insert(0, str(_models_dir))

from src.models.order import Order

logger = logging.getLogger(__name__)

ORDER_QUEUE = "order_processing"


class QueueProducer:
    """Одно соединение с RabbitMQ на несколько задач (в отличие от send_message)."""

    def __init__(self, host: str = "localhost"):
        self.host = host
        self.connection = None
        self.channel = None

    def connect(self) -> bool:
        """Подключение к RabbitMQ"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.host)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=ORDER_QUEUE, durable=True)
            return True
        except Exception as exc:
            logger.exception("Ошибка подключения к RabbitMQ: %s", exc)
            self.connection = None
            self.channel = None
            return False

    def _ensure_channel(self) -> bool:
        if self.channel and self.connection and self.connection.is_open:
            return True
        return self.connect()

    @staticmethod
    def _order_to_dict(order: Order) -> dict:
        """Снимок заказа из src.models.order.Order для тела сообщения."""
        items = []
        for product in order.products or []:
            if hasattr(product, "name"):
                items.append(
                    {
                        "name": product.name,
                        "quantity": getattr(product, "quantity", 1),
                        "price": getattr(product, "price", None),
                    }
                )
            else:
                items.append({"name": product})
        return {
            "user": getattr(order.user, "id", order.user),
            "items": items,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        }

    def send_order_task(
        self,
        order_id: Union[int, Order],
        task_type: str,
        data: Optional[dict] = None,
    ) -> bool:
        """Отправить задачу на обработку заказа"""
        payload = dict(data or {})
        if isinstance(order_id, Order):
            order = order_id
            payload = {**self._order_to_dict(order), **payload}
            order_id = order.order_id

        if order_id is None:
            logger.error("send_order_task: нет order_id")
            return False

        if not self._ensure_channel():
            return False

        try:
            message = {
                "task": task_type,
                "order_id": order_id,
                "retries": 0,
                **payload,
            }
            self.channel.basic_publish(
                exchange="",
                routing_key=ORDER_QUEUE,
                body=json.dumps(message, default=str),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            logger.info("Задача отправлена в очередь %s: %s", ORDER_QUEUE, message)
            return True
        except Exception as exc:
            logger.exception("Ошибка отправки задачи: %s", exc)
            self.channel = None
            return False

    def close(self):
        """Закрыть подключение"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        self.connection = None
        self.channel = None


def send_message(queue_name: str, message: dict):
    """Отправить сообщение в очередь"""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
    
    print(f"Сообщение отправлено в очередь {queue_name}")
    connection.close()

# Тест
if __name__ == "__main__":
    send_message('test_queue', {"test": "message"})
