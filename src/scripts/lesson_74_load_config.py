import os


def load_config():
    # Прочитай переменные окружения с типизацией и значениями по умолчанию
    config = {
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": os.getenv("DB_PORT", 27017),
        "DB_NAME": os.getenv("DB_NAME", "sfmshop"),
        "DB_USER": os.getenv("DB_USER", "admin"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD", "admin"),
    }
    return config


os.environ["DB_HOST"] = "production.host"
os.environ["DB_PORT"] = "27017"
os.environ["DB_NAME"] = "sfmshop"
os.environ["DB_USER"] = "admin"
os.environ["DB_PASSWORD"] = "admin"
print(load_config())
