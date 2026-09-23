# Файл src/services/queue_consumer.py
import json
import logging

import pika

logger = logging.getLogger(__name__)

ORDER_QUEUE = "order_processing"
ERROR_QUEUE = "order_processing_errors"


def send_email(message: dict) -> None:
    """Заглушка письма: в проекте нет SMTP-клиента."""
    logger.info(
        "send_email: заказ %s, email=%s",
        message.get("order_id"),
        message.get("user_email"),
    )


def update_stock(message: dict) -> None:
    """Заглушка склада: списание уже в транзакции POST /orders."""
    logger.info(
        "update_stock: заказ %s, items=%s",
        message.get("order_id"),
        message.get("items"),
    )


def generate_report(message: dict) -> None:
    """Заглушка отчёта: отдельного report-сервиса в проекте нет."""
    logger.info("generate_report: заказ %s", message.get("order_id"))


TASK_HANDLERS = {
    "send_email": send_email,
    "update_stock": update_stock,
    "generate_report": generate_report,
}


class QueueConsumer:
    """Обработка задач с повторами и очередью ошибок."""

    def __init__(self, host: str = "localhost", max_retries: int = 3):
        self.host = host
        self.connection = None
        self.channel = None
        self.max_retries = max_retries

    def connect(self):
        """Подключение к RabbitMQ."""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.host)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=ORDER_QUEUE, durable=True)
            self.channel.queue_declare(queue=ERROR_QUEUE, durable=True)
            self.channel.basic_qos(prefetch_count=1)
            return True
        except Exception as exc:
            logger.exception("Ошибка подключения к RabbitMQ: %s", exc)
            return False

    def _publish(self, queue_name: str, message: dict) -> None:
        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message, default=str),
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def _on_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)
        except Exception as exc:
            logger.exception("Некорректное сообщение, в %s: %s", ERROR_QUEUE, exc)
            try:
                self._publish(ERROR_QUEUE, {"raw": body.decode("utf-8", errors="replace")})
            except Exception:
                logger.exception("Не удалось положить сообщение в %s", ERROR_QUEUE)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        task = message.get("task")
        retries = int(message.get("retries", 0))
        handler = TASK_HANDLERS.get(task)

        try:
            if handler is None:
                raise ValueError(f"Неизвестная задача: {task}")
            handler(message)
        except Exception as exc:
            retries += 1
            message["retries"] = retries
            logger.exception(
                "Ошибка задачи %s заказа %s (попытка %s/%s): %s",
                task,
                message.get("order_id"),
                retries,
                self.max_retries,
                exc,
            )
            try:
                if retries < self.max_retries:
                    self._publish(ORDER_QUEUE, message)
                    logger.info("RETRY %s order=%s → %s", task, message.get("order_id"), ORDER_QUEUE)
                else:
                    self._publish(ERROR_QUEUE, message)
                    logger.error(
                        "DEAD %s order=%s → %s",
                        task,
                        message.get("order_id"),
                        ERROR_QUEUE,
                    )
            except Exception:
                logger.exception("Не удалось переотправить задачу %s", task)
        else:
            logger.info("OK %s order=%s", task, message.get("order_id"))

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self, queue_name: str = ORDER_QUEUE):
        """Слушать очередь order_processing."""
        if not self.connect():
            return
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self._on_message,
            auto_ack=False,
        )
        logger.info("QueueConsumer запущен для очереди %s", queue_name)
        self.channel.start_consuming()


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
