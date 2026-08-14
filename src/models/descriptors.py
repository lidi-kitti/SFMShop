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

class CachedProperty:
    """Дескриптор для кеширования свойств"""
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return self
       # Проверка кэша
        cache_attr = f"_cached_{self.name}"
        if hasattr(instance, cache_attr):
            return getattr(instance, cache_attr)

        # Вычисление и кэширование
        value = self.func(instance)
        setattr(instance, cache_attr, value)
        return value