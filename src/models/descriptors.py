# Файл src/models/descriptors.py
class PositiveNumber:
    """Дескриптор для валидации положительных чисел"""
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError(f"Значение {self.name} должно быть положительным")
        instance.__dict__[self.name] = value