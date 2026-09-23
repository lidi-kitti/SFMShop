# Файл src/services/queue_producer.py
import json
import logging

import pika

logger = logging.getLogger(__name__)

ORDER_QUEUE = "order_processing"


class QueueProducer:
    """Одно соединение с RabbitMQ на несколько задач."""

    def __init__(self, host: str = "localhost"):
        self.host = host
        self.connection = None
        self.channel = None

    def connect(self):
        """Подключение к RabbitMQ."""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.host)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=ORDER_QUEUE, durable=True)
            return True
        except Exception as exc:
            logger.exception("Ошибка подключения к RabbitMQ: %s", exc)
            return False

    def send_order_task(self, order_id: int, task_type: str, data: dict):
        """Отправить задачу в очередь order_processing."""
        if not self.channel:
            if not self.connect():
                return False

        try:
            message = {
                "task": task_type,
                "order_id": order_id,
                "retries": 0,
                **data,
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
            return False

    def close(self):
        """Закрыть подключение."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()


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
