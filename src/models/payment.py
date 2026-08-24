from mixins import LoggableMixin, SerializableMixin
from abc import ABC, abstractmethod

class Payment(ABC):
    @abstractmethod
    def process(self):
        pass

class CardPayment(LoggableMixin, SerializableMixin, Payment):
    def __init__(self, amount):
        self.amount = amount
        self.log(f"Создан платеж: {amount}")
    
    def process(self):
        self.log("Обработка платежа")
        return True
    
    def to_json(self):
        return {"type": "CardPayment", "amount": self.amount}

# Проверка MRO
print(CardPayment.mro())
payment = CardPayment(100)
print(payment.to_json())