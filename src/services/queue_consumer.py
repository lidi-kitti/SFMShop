# Файл src/services/queue_consumer.py
#
# Масштабирование: prefetch_count=1 (basic_qos) — competing consumers.
# Запусти несколько процессов на одну очередь order_processing:
#   python -c "from src.services.queue_consumer import QueueConsumer; QueueConsumer().start_consuming()"
# Брокер отдаёт каждое сообщение одному воркеру. +N процессов = +N воркеров.
# Подробнее: docs/message_queue_architecture.md (раздел «Масштабирование»).
#
import json
import logging
import os
import sys
import time
import traceback
from pathlib import Path

import pika
from pymongo import MongoClient

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.services.log_service import LogService

logger = logging.getLogger(__name__)

ORDER_QUEUE = "order_processing"
ERROR_QUEUE = "order_processing_errors"


def _get_log_service() -> LogService | None:
    try:
        svc = LogService()
        # Mongo не обязателен для разбора очереди: короткий timeout, без 30 с ожидания
        svc.client = MongoClient(
            host=os.getenv("MONGO_HOST", "localhost"),
            port=int(os.getenv("MONGO_PORT", 27017)),
            serverSelectionTimeoutMS=400,
            connectTimeoutMS=400,
        )
        svc.collection = svc.client[svc.DB_NAME][svc.COLLECTION_NAME]
        return svc
    except Exception as exc:
        logger.warning("LogService недоступен, пишем только в консоль: %s", exc)
        return None


log_service = _get_log_service()


def _disable_mongo(reason: str) -> None:
    global log_service
    if log_service is None:
        return
    logger.warning("%s — дальше только консоль", reason)
    log_service = None


def _log_op(message: str, **fields) -> None:
    logger.info(message)
    if log_service is None:
        return
    try:
        log_service.save_log({"type": "access", "message": message, **fields})
    except Exception as exc:
        _disable_mongo(f"MongoDB недоступна ({exc})")


def _log_error(message: str, exc: Exception | None = None) -> None:
    logger.error(message, exc_info=exc is not None)
    if log_service is None:
        return
    try:
        log_service.log_error(
            message,
            stack_trace=traceback.format_exc() if exc else None,
        )
    except Exception as mongo_exc:
        _disable_mongo(f"MongoDB недоступна ({mongo_exc})")


def send_email(message: dict) -> None:
    """Отправка email-уведомления о заказе (SMTP в проекте нет)."""
    _log_op(
        f"send_email: заказ {message.get('order_id')} → {message.get('user_email')}",
        task="send_email",
        order_id=message.get("order_id"),
    )


def update_stock(message: dict) -> None:
    """Фоновое обновление склада / кэша (списание stock уже в POST /orders)."""
    _log_op(
        f"update_stock: заказ {message.get('order_id')}, items={message.get('items')}",
        task="update_stock",
        order_id=message.get("order_id"),
    )


def generate_report(message: dict) -> None:
    """Генерация отчёта по заказу."""
    _log_op(
        f"generate_report: заказ {message.get('order_id')}",
        task="generate_report",
        order_id=message.get("order_id"),
    )


TASK_HANDLERS = {
    "send_email": send_email,
    "update_stock": update_stock,
    "generate_report": generate_report,
}


class QueueConsumer:
    """Одно соединение, prefetch=1, retry 3 раза, DLQ order_processing_errors."""

    def __init__(self, host: str = "localhost"):
        self.host = host
        self.connection = None
        self.channel = None
        self.max_retries = 3

    def connect(self) -> bool:
        """Подключение к RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.host)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=ORDER_QUEUE, durable=True)
            self.channel.queue_declare(queue=ERROR_QUEUE, durable=True)
            self.channel.basic_qos(prefetch_count=1)
            _log_op("QueueConsumer подключён к RabbitMQ", queue=ORDER_QUEUE)
            return True
        except Exception as exc:
            _log_error(f"Ошибка подключения к RabbitMQ: {exc}", exc)
            self.connection = None
            self.channel = None
            return False

    def _publish(self, queue_name: str, message: dict) -> None:
        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message, default=str),
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def process_message(self, ch, method, properties, body):
        """Обработка сообщения с retry-логикой"""
        try:
            message = json.loads(body)
        except Exception as exc:
            _log_error(f"Некорректное сообщение, в {ERROR_QUEUE}: {exc}", exc)
            try:
                self._publish(
                    ERROR_QUEUE,
                    {"raw": body.decode("utf-8", errors="replace")},
                )
            except Exception as publish_exc:
                _log_error(f"Не удалось положить сообщение в {ERROR_QUEUE}", publish_exc)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        task = message.get("task")
        retries = int(message.get("retries", 0))
        handler = TASK_HANDLERS.get(task)
        _log_op(
            f"Получено task={task} order={message.get('order_id')} attempt={retries + 1}",
            task=task,
            order_id=message.get("order_id"),
        )

        try:
            if handler is None:
                raise ValueError(f"Неизвестная задача: {task}")
            handler(message)
        except Exception as exc:
            retries += 1
            message["retries"] = retries
            _log_error(
                f"Ошибка задачи {task} заказа {message.get('order_id')} "
                f"(попытка {retries}/{self.max_retries}): {exc}",
                exc,
            )
            try:
                if retries < self.max_retries:
                    time.sleep(2 ** (retries - 1))
                    self._publish(ORDER_QUEUE, message)
                    _log_op(
                        f"RETRY {task} order={message.get('order_id')} → {ORDER_QUEUE}",
                        task=task,
                        order_id=message.get("order_id"),
                    )
                else:
                    self._publish(ERROR_QUEUE, message)
                    _log_error(
                        f"DEAD {task} order={message.get('order_id')} → {ERROR_QUEUE}",
                        exc,
                    )
            except Exception as publish_exc:
                _log_error(f"Не удалось переотправить задачу {task}", publish_exc)
        else:
            _log_op(f"OK {task} order={message.get('order_id')}", task=task)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        """Запуск обработки сообщений"""
        if not self.connect():
            return
        self.channel.basic_consume(
            queue=ORDER_QUEUE,
            on_message_callback=self.process_message,
            auto_ack=False,
        )
        _log_op(f"QueueConsumer слушает {ORDER_QUEUE} (prefetch=1)")
        self.channel.start_consuming()

    def start(self, queue_name: str = ORDER_QUEUE):
        """Алиас для start_consuming (очередь всегда order_processing)."""
        self.start_consuming()


def process_message(ch, method, properties, body):
    """Обработка сообщения"""
    message = json.loads(body)
    print(f"Получено сообщение: {message}")
    task = message.get('task')
    if task == "process_order":
        order_id = message.get('order_id')
        print(f"Обработка заказа {order_id}")
    elif task == "process_payment":
        payment_id = message.get('payment_id')
        print(f"Обработка платежа {payment_id}")
    elif task == "process_shipping":
        shipping_id = message.get('shipping_id')
        print(f"Обработка доставки {shipping_id}")
    else:
        print(f"Неизвестная задача: {task}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer(queue_name: str):
    """Запуск consumer"""
    # Твой код здесь
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=False)
    print(f"Consumer запущен для очереди {queue_name}")
    channel.start_consuming()
    

# Тест
if __name__ == "__main__":
    start_consumer('test_queue')
