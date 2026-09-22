# Файл src/services/order_service.py (добавь в начало файла)
# Архитектура системы с брокером сообщений для проекта SFMShop:
#
# Клиент ──POST /orders──► FastAPI (Producer)
#                              │
#                    COMMIT в PostgreSQL (заказ + stock)
#                              │
#                              ▼
#                    Redis-очередь (брокер)
#                     email | warehouse | report
#                              │
#                              ▼
#                    Consumer (queue_consumer.py)
#                    retry / dead-letter
#
# 1. Producer (src/api/main.py):
# - После успешного COMMIT заказа (create_order) не держит HTTP-запрос
#   на SMTP, отчёт и прочий фон — кладёт задачи в очередь.
# - Задачи: отправка email, обновление склада (кэш/уведомление склада),
#   генерация отчета.
# - Списание остатка в транзакции остаётся синхронным на primary:
#   очередь не заменяет ACID. Брокер — только побочные эффекты.
# - Сейчас в коде фон ещё можно запустить через BackgroundTasks
#   (POST /orders/process-background). Очередь переживает рестарт
#   uvicorn, BackgroundTasks — нет.
#
# 2. Очередь сообщений:
# - Хранит задачи для обработки (Redis List/Stream: LPUSH/BRPOP или
#   XADD/XREADGROUP), отдельно от PostgreSQL-заказов.
# - Обеспечивает надежность доставки: сообщение живёт в брокере, пока
#   consumer не подтвердит обработку; при пике заказов сглаживает нагрузку.
# - Не источник истины: заказ уже в БД. Потеря очереди ≠ потеря заказа,
#   но письмо/отчёт можно поставить повторно.
#
# 3. Consumer (src/services/queue_consumer.py):
# - Получает задачи из очереди (несколько воркеров, как в
#   producer_consumer.py: Queue + workers).
# - Обрабатывает задачи в фоне, не блокируя витрину и checkout.
# - Обрабатывает ошибки и retry: экспоненциальная пауза, после лимита —
#   dead-letter; идемпотентность (повтор email не должен слать дважды).
#
from abc import ABC, abstractmethod
from src.models.order import Order
from src.services.order_validator import OrderValidator
from src.services.order_calculator import OrderCalculator, DiscountStrategy

class NotificationService(ABC):
    @abstractmethod
    def send(self, order: Order):
        pass

class Database(ABC):
    @abstractmethod
    def save(self, order: Order):
        pass
class OrderService:
    """Сервис для обработки заказов (DIP)"""
    def __init__(self, notification_service: NotificationService, database: Database):
        self.notification_service = notification_service
        self.database = database
    
    def process_order(self, order: Order, discount: DiscountStrategy = None):
        """Обработка заказа"""
        OrderValidator.validate(order)
        total = OrderCalculator.calculate_total(order)
        if discount:
            total = OrderCalculator.apply_discount(order, discount)
        self.notification_service.send(order)
        self.database.save(order)
        return total