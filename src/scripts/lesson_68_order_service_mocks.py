# Создай файл scripts/lesson_68_order_service_mocks.py
from unittest.mock import MagicMock


class OrderService:
    """Оформляет заказ: пишет в БД и шлёт уведомление."""

    def __init__(self, db, notifier):
        self.db = db
        self.notifier = notifier

    def place_order(self, user_id, items):
        # items: список (product_id, qty, price)
        if not items:
            raise ValueError("Пустой заказ")
        total = sum(qty * price for _, qty, price in items)
        order_id = self.db.create_order(user_id=user_id, total=total)
        self.notifier.send(user_id=user_id, text=f"Заказ #{order_id} на {total} руб.")
        return order_id


def test_happy_path():
    db = MagicMock()
    notifier = MagicMock()
    db.create_order.return_value = 42
    service = OrderService(db, notifier)

    order_id = service.place_order(1, [(10, 2, 500)])

    assert order_id == 42
    db.create_order.assert_called_once_with(user_id=1, total=1000)
    notifier.send.assert_called_once_with(user_id=1, text="Заказ #42 на 1000 руб.")
    print(f"happy_path: ok, order_id = {order_id}")


def test_empty_raises():
    db = MagicMock()
    notifier = MagicMock()
    service = OrderService(db, notifier)

    try:
        service.place_order(1, [])
    except ValueError as exc:
        assert str(exc) == "Пустой заказ"
    else:
        raise AssertionError("ожидался ValueError")

    db.create_order.assert_not_called()
    notifier.send.assert_not_called()
    print("empty_raises: ok, БД и уведомление не дёрнуты")


def test_db_failure():
    db = MagicMock()
    notifier = MagicMock()
    db.create_order.side_effect = RuntimeError("БД недоступна")
    service = OrderService(db, notifier)

    try:
        service.place_order(1, [(10, 1, 100)])
    except RuntimeError:
        pass
    else:
        raise AssertionError("ожидался RuntimeError")

    notifier.send.assert_not_called()
    print("db_failure: ok, уведомление не ушло при падении БД")


if __name__ == "__main__":
    test_happy_path()
    test_empty_raises()
    test_db_failure()
    print("Все тесты прошли")
