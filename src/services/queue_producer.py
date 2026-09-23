# Файл src/services/queue_producer.py
import pika
import json


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