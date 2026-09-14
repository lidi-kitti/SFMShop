class ServiceRegistry:
    """Реестр сервисов: регистрирует сервисы и маршрутизирует к ним запросы."""
    def __init__(self):
        self._services = {}

    def register(self, name, handler):
        self._services[name] = handler

    def call(self, name, action, payload):
        if name not in self._services:
            raise ValueError(f"Service {name} not found")
        return self._services[name](action, payload)


class PaymentService:
    """Сервис обработки платежей."""
    def __call__(self, action, payload):
        if action == "process":
            amount = payload["amount"]
            if amount <= 0:
                return {"status": "rejected", "reason": "amount must be positive"}
            return {"status": "paid", "amount": amount}
        raise ValueError(f"Неизвестное действие: {action}")

class OrderService:
    """Сервис обработки заказов."""
    def __init__(self, registry):
        self.registry = registry

    def __call__(self, action, payload):
        if action == "create":
            total = sum(item["price"] * item["qty"] for item in payload["items"])
            payment = self.registry.call("payment", "process", {"amount": total})
            status = "confirmed" if payment["status"] == "paid" else "failed"
            return {"order_id": payload["order_id"], "total": total, "status": status}
        raise ValueError(f"Неизвестное действие: {action}")

def main():
    registry = ServiceRegistry()
    registry.register("payment", PaymentService())
    registry.register("order", OrderService(registry))

    orders = [
        {"order_id": 101, "items": [{"name": "Худи SFM", "price": 2500, "qty": 2},
                                    {"name": "Кепка SFM", "price": 1200, "qty": 1}]},
        {"order_id": 102, "items": [{"name": "Стикерпак", "price": 0, "qty": 3}]},
    ]

    for order in orders:
        result = registry.call("order", "create", order)
        print(f"Заказ {result['order_id']}: сумма {result['total']}, статус {result['status']}")

    try:
        registry.call("delivery", "ship", {})
    except KeyError as e:
        print(f"Ошибка маршрутизации: {e}")


if __name__ == "__main__":
    main()