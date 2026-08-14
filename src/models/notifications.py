from abc import ABC, abstractmethod


class Notification(ABC):
    """Абстрактный класс для уведомлений"""

    @abstractmethod
    def send(self, message: str=None):
        """Отправить уведомление"""
        pass


class EmailNotification(Notification):
    """Уведомление по email"""

    def __init__(self, email: str=''):
        self.email = email

    def send(self, message: str=None):
        """Отправить email"""
        if message is None:
            message = 'Нет сообщения'
        print(f'Отправка email на {self.email}: {message}')


class SMSNotification(Notification):
    """Уведомление по SMS"""

    def __init__(self, phone: str=''):
        self.phone = phone

    def send(self, message: str=None):
        """Отправить SMS"""
        if message is None:
            message = 'Нет сообщения'
        print(f'Отправка SMS на {self.phone}: {message}')
