class LoggableMixin:
    """Миксин для логирования"""

    def log(self, message: str):
        """Логировать сообщение с именем класса"""
        class_name = self.__class__.__name__
        print(f"[{class_name}] {message}")


class ValidatableMixin:
    """Миксин для валидации данных"""

    def validate(self):
        """Валидировать данные (переопределяется в дочерних классах)"""
        return True

    def is_valid(self):
        """Проверить, валидны ли данные"""
        try:
            self.validate()
            return True
        except ValueError:
            return False


class SerializableMixin:
    """Миксин для JSON-сериализации"""

    def to_json(self):
        """Преобразовать объект в JSON"""
        return {
            "class": self.__class__.__name__,
            "data": self.__dict__,
        }
