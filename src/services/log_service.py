import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class LogService:
    """Логи в MongoDB: запись документов и выборки по полям."""

    DB_NAME = "sfmshop_logs"
    COLLECTION_NAME = "logs"

    def __init__(self, host=None, port=None, db_name=None):
        self.client = MongoClient(
            host=host or os.getenv("MONGO_HOST", "localhost"),
            port=int(port or os.getenv("MONGO_PORT", 27017)),
        )
        self.collection = self.client[db_name or self.DB_NAME][self.COLLECTION_NAME]

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


if __name__ == "__main__":
    log_service = LogService()

    stats = log_service.get_logs_statistics()
    print(f"Статистика: {stats}")

    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    error_logs = log_service.get_error_logs(since=yesterday)
    print(f"Ошибок за сутки: {len(error_logs)}")

    access_logs = log_service.get_access_logs(since=yesterday)
    print(f"Обращений за сутки: {len(access_logs)}")

    today_logs = log_service.get_logs_by_date_range(yesterday, datetime.now(timezone.utc))
    print(f"Логов за сегодня: {len(today_logs)}")
