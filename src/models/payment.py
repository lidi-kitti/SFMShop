class Payment:

    def __init__(self, amount):
        self.amount = amount

    def process(self, amount):
        print(f'Базовая обработка платежа на {amount}')

    def process_payment(self):
        raise NotImplementedError('Метод должен быть переопределен в дочернем классе')


class Loggable:

    def log(self, message):
        print(f'[LOG] {message}')


class Refundable:

    def refund(self, amount):
        print(f'Возврат {amount} на счёт')


class CardPayment(Payment, Loggable, Refundable):

    def __init__(self, amount, card_number):
        super().__init__(amount)
        self.__card_number = card_number

    def process(self, amount):
        self.log('начало платежа')
        super().process(amount)
        return True

    def process_payment(self):
        masked_card = '**** ' + self.__card_number[-4:]
        return 'Оплата картой ' + masked_card + ': ' + str(self.amount) + ' руб.'


class PayPalPayment(Payment):
    def __init__(self, amount, email):
        super().__init__(amount)
        self.email = email

    def process_payment(self):
        return "Оплата PayPal (" + self.email + "): " + str(self.amount) + " руб."
