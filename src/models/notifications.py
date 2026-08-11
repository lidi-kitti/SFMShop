# Файл src/models/notifications.py
from abc import ABC, abstractmethod


class Notification(ABC):
    """Абстрактный класс для уведомлений"""

    @abstractmethod
    def send(self, message: str) -> None:
        """Отправить уведомление"""
        pass


class EmailNotification(Notification):
    """Уведомление по email"""

    def __init__(self, email: str):
        self.email = email

    def send(self, message: str) -> None:
        print(f"Отправляем уведомление на email: {self.email}")
        print(f"Сообщение: {message}")


class SMSNotification(Notification):
    """Уведомление по SMS"""

    def __init__(self, phone: str):
        self.phone = phone

    def send(self, message: str) -> None:
        print(f"Отправляем уведомление на телефон: {self.phone}")
        print(f"Сообщение: {message}")


def send_notification(notification: Notification, message: str) -> None:
    """Отправить уведомление"""
    notification.send(message)


if __name__ == "__main__":
    email_notifications = [
        EmailNotification("test@example.com"),
        EmailNotification("test2@example.com"),
        EmailNotification("test3@example.com"),
        EmailNotification("test4@example.com"),
        EmailNotification("test5@example.com"),
        EmailNotification("test6@example.com"),
        EmailNotification("test7@example.com"),
        EmailNotification("test8@example.com"),
        EmailNotification("test9@example.com"),
        EmailNotification("test10@example.com"),
    ]
    sms_notifications = [
        SMSNotification("+79991234567"),
        SMSNotification("+79991234568"),
        SMSNotification("+79991234569"),
        SMSNotification("+79991234570"),
        SMSNotification("+79991234571"),
        SMSNotification("+79991234572"),
        SMSNotification("+79991234573"),
        SMSNotification("+79991234574"),
        SMSNotification("+79991234575"),
        SMSNotification("+79991234576"),
        SMSNotification("+79991234577"),
    ]
    for notification in email_notifications:
        send_notification(notification, "Тестовое уведомление по email")
    for notification in sms_notifications:
        send_notification(notification, "Тестовое уведомление по SMS")
