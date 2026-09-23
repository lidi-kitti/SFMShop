# Файл src/services/queue_consumer.py
import pika
import json


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
    channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=True)
    print(f"Consumer запущен для очереди {queue_name}")
    channel.start_consuming()
    

# Тест
if __name__ == "__main__":
    start_consumer('test_queue')
