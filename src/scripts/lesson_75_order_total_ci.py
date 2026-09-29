# Создай файл scripts/lesson_75_order_total_ci.py
import io
import unittest


def order_total(items, discount_percent=0):
    """items: список (цена, количество). Вернуть сумму со скидкой,
    округлённую до 2 знаков. discount_percent в диапазоне 0..100."""
    if not 0 <= discount_percent <= 100:
        raise ValueError("Скидка должна быть в диапазоне 0..100")
    subtotal = sum(price * quantity for price, quantity in items)
    return round(subtotal * (1 - discount_percent / 100), 2)


class TestOrderTotal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(order_total([(100, 2), (50, 1)]), 250.0)
        self.assertEqual(order_total([(10.5, 2)]), 21.0)

    def test_with_discount(self):
        self.assertEqual(order_total([(100, 2)], discount_percent=10), 180.0)
        self.assertEqual(order_total([(200, 1), (50, 2)], discount_percent=100), 0.0)

    def test_empty_order(self):
        self.assertEqual(order_total([]), 0.0)
        self.assertEqual(order_total([], discount_percent=15), 0.0)

    def test_invalid_discount(self):
        with self.assertRaises(ValueError):
            order_total([(100, 1)], discount_percent=-1)
        with self.assertRaises(ValueError):
            order_total([(100, 1)], discount_percent=101)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOrderTotal)
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("CI статус: PASS" if result.wasSuccessful() else "CI статус: FAIL")
