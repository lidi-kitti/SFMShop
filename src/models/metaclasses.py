class ModelMeta(type):
    """Метакласс для автоматического добавления методов"""

    def __new__(cls, name, bases, attrs):
        """Вызывается при создании класса"""
        # Добавить метод to_dict() ко всем классам
        def to_dict(self):
            """Преобразовать объект в словарь"""
            return self.__dict__

        attrs["to_dict"] = to_dict

        # Создать класс
        return super().__new__(cls, name, bases, attrs)
