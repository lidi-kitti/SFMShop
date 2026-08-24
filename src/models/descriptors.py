"""Дескрипторы для валидации полей моделей SFMShop.

Урок 39 (ba7): Дескрипторы в Python.
Дескриптор — объект, реализующий протокол __get__/__set__/__set_name__,
который управляет доступом к атрибуту и позволяет переиспользовать валидацию
между классами без дублирования кода в сеттерах.
"""


class PositiveNumber:
    """Дескриптор для валидации положительных чисел"""

    def __init__(self, name=None):
        self.name = name  # Имя атрибута в instance.__dict__

    def __set_name__(self, owner, name):
        if self.name is None or self.name == name:
            self.name = "_" + name

    def __get__(self, instance, owner):
        """Получение значения"""
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        """Установка значения с валидацией"""
        if value < 0:
            raise ValueError(f"{self.name} не может быть отрицательным")
        instance.__dict__[self.name] = value


class EmailDescriptor:
    """Дескриптор для валидации email"""

    def __set_name__(self, owner, name):
        self.storage_name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        if "@" not in value or "." not in value:
            raise ValueError("Неверный формат email")
        setattr(instance, self.storage_name, value)


class AgeDescriptor:
    """Дескриптор для валидации возраста"""

    def __set_name__(self, owner, name):
        self.storage_name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        if value < 0 or value > 150:
            raise ValueError("Возраст должен быть от 0 до 150")
        setattr(instance, self.storage_name, value)

class CachedProperty:
    """Дескриптор для кеширования свойств (используется как @CachedProperty)"""

    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        cache_attr = f"_cached_{self.name}"
        if cache_attr in instance.__dict__:
            return instance.__dict__[cache_attr]
        value = self.func(instance)
        instance.__dict__[cache_attr] = value
        return value