from src.models.exceptions import ValidationError


class User:
    def __init__(self, name, email):
        self.name = name
        self._email = email

    def set_email(self, email):
        #Проверка формата почты
        if "@" not in email:
            raise ValidationError("Неверный формат email")
        self._email = email