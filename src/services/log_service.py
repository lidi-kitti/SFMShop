import importlib
import importlib.util
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LOG_DIR = _PROJECT_ROOT / "logs"
_LOG_FILE = _LOG_DIR / "sfmshop.log"
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"


class LogService:
    """Логи: файл + консоль (пять уровней) и документы в MongoDB."""

    DB_NAME = "sfmshop_logs"
    COLLECTION_NAME = "logs"
    LOGGER_NAME = "sfmshop"

    def __init__(self, host=None, port=None, db_name=None):
        self.client = MongoClient(
            host=host or os.getenv("MONGO_HOST", "localhost"),
            port=int(port or os.getenv("MONGO_PORT", 27017)),
            serverSelectionTimeoutMS=2000,
        )
        self.collection = self.client[db_name or self.DB_NAME][self.COLLECTION_NAME]
        self.logger = self._configure_logger()

    def _configure_logger(self) -> logging.Logger:
        """Один формат на FileHandler и StreamHandler, уровни от DEBUG."""
        logger = logging.getLogger(self.LOGGER_NAME)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        if logger.handlers:
            return logger

        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
        return logger

    @staticmethod
    def _format_message(message: str, **kwargs) -> str:
        if not kwargs:
            return message
        extras = " ".join(f"{key}={value}" for key, value in kwargs.items())
        return f"{message} | {extras}"

    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_message(message, **kwargs))

    def info(self, message: str, **kwargs):
        self.logger.info(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs):
        self.logger.error(self._format_message(message, **kwargs))

    def critical(self, message: str, **kwargs):
        """CRITICAL: запись в лог и алерт (в продакшене — Sentry)."""
        formatted = self._format_message(message, **kwargs)
        self.logger.critical(formatted)
        self.send_alert(formatted)

    def send_alert(self, message: str, **kwargs) -> None:
        """Алерт при CRITICAL.

        В продакшене: sentry_sdk.init(dsn=SENTRY_DSN) и
        sentry_sdk.capture_message(message, level="fatal")
        (или capture_exception при исключении).
        """
        formatted = self._format_message(message, **kwargs)
        self.logger.critical("ALERT: %s", formatted)
        sentry_dsn = os.getenv("SENTRY_DSN")
        if not sentry_dsn:
            return
        if importlib.util.find_spec("sentry_sdk") is None:
            self.logger.warning(
                "SENTRY_DSN задан, но пакет sentry-sdk не установлен — алерт только в лог"
            )
            return
        sentry_sdk = importlib.import_module("sentry_sdk")
        sentry_sdk.capture_message(formatted, level="fatal")

    def _now(self):
        return datetime.now(timezone.utc)

    def save_log(self, log_data):
        document = dict(log_data)
        if "timestamp" not in document:
            document["timestamp"] = self._now()
        result = self.collection.insert_one(document)
        return result.inserted_id

    def log_error(self, message: str, stack_trace: Optional[str] = None):
        return self.save_log({
            "type": "error",
            "message": message,
            "stack_trace": stack_trace,
        })

    def log_access(self, ip: str, endpoint: str, method: str, status_code: int):
        return self.save_log({
            "type": "access",
            "ip": ip,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
        })

    def get_logs_by_type(self, log_type, since: Optional[datetime] = None):
        query = {"type": log_type}
        if since:
            query["timestamp"] = {"$gte": since}
        return list(self.collection.find(query))

    def get_error_logs(self, since: Optional[datetime] = None):
        return self.get_logs_by_type("error", since=since)

    def get_access_logs(self, since: Optional[datetime] = None):
        return self.get_logs_by_type("access", since=since)

    def get_logs_by_status_code(self, min_status, max_status):
        return list(
            self.collection.find({
                "status_code": {"$gte": min_status, "$lt": max_status},
            })
        )

    def get_logs_by_date_range(self, start_date, end_date):
        return list(
            self.collection.find({
                "timestamp": {"$gte": start_date, "$lte": end_date},
            })
        )

    def get_logs_by_ip(self, ip):
        return list(self.collection.find({"ip": ip}))

    def get_all_logs(self):
        """Все документы коллекции logs."""
        return list(self.collection.find({}))

    def get_logs_statistics(self):
        type_stats = self.collection.aggregate([
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
        ])
        status_stats = self.collection.aggregate([
            {"$group": {"_id": "$status_code", "count": {"$sum": 1}}},
        ])
        return {
            "by_type": list(type_stats),
            "by_status": list(status_stats),
            "total": self.collection.count_documents({}),
        }


log_service = LogService()


def log_order_created(order_id: int):
    """Логирование создания заказа"""
    log_service.info(f"Заказ создан: order_id={order_id}")


def log_order_error(error: str):
    """Логирование ошибки заказа"""
    log_service.error(f"Ошибка обработки заказа: {error}")


# Тестирование
if __name__ == "__main__":
    log_service.debug("Проверка уровня DEBUG")
    log_service.info("Проверка уровня INFO")
    log_service.warning("Проверка уровня WARNING")
    log_service.error("Проверка уровня ERROR")
    log_service.critical("Проверка уровня CRITICAL: сбой логирования")

    try:
        error_log = {
            "type": "error",
            "message": "Ошибка подключения к БД",
            "stack_trace": "Traceback (most recent call last)...",
            "timestamp": datetime.now(timezone.utc),
        }
        error_id = log_service.save_log(error_log)
        print(f"Лог ошибки сохранен: {error_id}")

        access_log = {
            "type": "access",
            "ip": "192.168.1.1",
            "endpoint": "/api/products",
            "method": "GET",
            "status_code": 200,
            "timestamp": datetime.now(timezone.utc),
        }
        access_id = log_service.save_log(access_log)
        print(f"Лог доступа сохранен: {access_id}")

        all_logs = log_service.get_all_logs()
        print(f"Всего логов: {len(all_logs)}")

        error_logs = log_service.get_logs_by_type("error")
        print(f"Логов ошибок: {len(error_logs)}")
    except Exception as exc:
        print(
            "MongoDB недоступна на localhost:27017. "
            "Запусти mongod и повтори. "
            f"Детали: {exc.__class__.__name__}"
        )
