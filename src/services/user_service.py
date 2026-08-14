from abc import ABC, abstractmethod
from src.models.user import User

class UserValidator:
    """Класс для валидации пользователя (SRP)"""
    @staticmethod
    def validate(user: User) -> bool:
        """Валидация пользователя"""
        if not user.name:
            raise ValueError("Имя не может быть пустым")
        if "@" not in user.email:
            raise ValueError("Email должен содержать @")
        if user.age < 18:
            raise ValueError("Пользователь должен быть старше 18 лет")
        if user.balance < 0:
            raise ValueError("Баланс не может быть отрицательным")
        return True

class UserCalculator:
    """Класс для расчетов пользователя (SRP)"""
    @staticmethod
    def calculate_total_spent(user: User) -> float:
        """Расчет общей потраченной суммы"""
        total = 0
        for order in user.orders:
            total += order.total
        return total

class DiscountStrategy(ABC):
    """Абстрактный класс для стратегии скидки (OCP)"""
    @abstractmethod
    def apply(self, balance: float) -> float:
        pass

class PercentDiscount(DiscountStrategy):
    """Процентная скидка"""
    def __init__(self, percent: float):
        self.percent = percent
    
    def apply(self, balance: float) -> float:
        return balance * (1 + self.percent / 100)

class FixedDiscount(DiscountStrategy):
    """Фиксированная скидка"""
    def __init__(self, amount: float):
        self.amount = amount
    
    def apply(self, balance: float) -> float:
        return balance + self.amount

class NotificationService(ABC):
    """Абстрактный класс для уведомлений (DIP)"""
    @abstractmethod
    def send(self, user: User, message: str):
        pass

class EmailNotificationService(NotificationService):
    """Реализация email уведомлений"""
    def send(self, user: User, message: str):
        print(f"Отправка email на {user.email}: {message}")

class Database(ABC):
    """Абстрактный класс для БД (DIP)"""
    @abstractmethod
    def save(self, user: User):
        pass

class PostgreSQLDatabase(Database):
    """Реализация PostgreSQL"""
    def save(self, user: User):
        print(f"Сохранение пользователя {user.user_id} в PostgreSQL")

class UserService:
    """Сервис для обработки пользователей (DIP)"""
    def __init__(self, notification_service: NotificationService, database: Database):
        self.notification_service = notification_service
        self.database = database
    
    def register_user(self, user: User):
        """Регистрация пользователя"""
        UserValidator.validate(user)
        self.notification_service.send(user, f"Добро пожаловать, {user.name}!")
        self.database.save(user)
    
    def generate_user_report(self, user: User) -> str:
        """Генерация отчета о пользователе (SRP)"""
        total_spent = UserCalculator.calculate_total_spent(user)
        report = f"Пользователь: {user.name}\n"
        report += f"Email: {user.email}\n"
        report += f"Всего заказов: {len(user.orders)}\n"
        report += f"Потрачено: {total_spent}\n"
        return report