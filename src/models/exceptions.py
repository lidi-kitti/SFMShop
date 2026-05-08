
class SFMShopException(Exception):
    pass

class ValidationError(SFMShopException):
    """для ошибок валидации"""
    pass

class BusinessLogicError(SFMShopException):
    """для ошибок бизнес-логики"""
    pass

