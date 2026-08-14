# Файл src/models/metaclasses.py
class ModelMeta(type):
    """Метакласс, который автоматически регистрирует классы моделей в реестре"""
    _registry = {}
    
    def __new__(cls, name, bases, attrs):
        def to_dict(self):
            return self.__dict__

        attrs["to_dict"] = to_dict
        
        new_class = super().__new__(cls, name, bases, attrs)
        if name != "Model":
            cls._registry[name] = new_class
        return new_class