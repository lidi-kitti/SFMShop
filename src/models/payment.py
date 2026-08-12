
class Payment:
    def __init__(self, amount):
        self.amount = amount

    def process_payment(self):
        raise NotImplementedError("Метод должен быть переопределен")

    def process(self):
        print("Payment.process()")

class Loggable:
    def log(self):
        print("Loggable.log()")



class CardPayment(Payment, Loggable):
    def __init__(self, amount, card_number):
        super().__init__(amount)
        self.__card_number = card_number
    def process(self):
        print("CardPayment.process()")
        self.log()
        super().process()

    def process_payment(self):
        return f"Оплата картой **** {self.__card_number[-4:]}: {self.amount} руб."

class PayPalPayment(Payment):
    def __init__(self, amount, email):
        super().__init__(amount)
        self._email = email

    def process_payment(self):
        return f"Оплата PayPal ({self._email}): {self.amount} руб."

# Просмотр MRO
print("MRO для CardPayment:")
for i, cls in enumerate(CardPayment.mro(), 1):
    print(f"{i}. {cls.__name__}")

# Использование
payment = CardPayment(1000, "1234567890123456")
payment.process()

class A:
    def method(self):
        print("A.method()")

class B(A):
    def method(self):
        print("B.method()")
        super().method()

class C(A):
    def method(self):
        print("C.method()")
        super().method()

class D(B, C):
    def method(self):
        print("D.method()")
        super().method()

# Просмотр MRO
print("MRO для D:")
for i, cls in enumerate(D.mro(), 1):
    print(f"{i}. {cls.__name__}")

# Использование
d = D()
d.method()