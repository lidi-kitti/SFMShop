# Создай файл scripts/lesson_66_order_unittest.py
import io
import unittest


class Order:
    """Заказ SFMShop: считает итог корзины и применяет скидку."""

    def __init__(self, items):
        # items: список (цена, количество)
        self.items = items

    def subtotal(self):
        return sum(price * quantity for price, quantity in self.items)

    def apply_discount(self, rate):
        if not 0 <= rate <= 0.5:
            raise ValueError("Скидка должна быть от 0 до 0.5")
        return self.subtotal() * (1 - rate)


class TestOrder(unittest.TestCase):
    def test_subtotal(self):
        order = Order([(1000, 2), (500, 1)])
        self.assertEqual(order.subtotal(), 2500)

    def test_apply_discount(self):
        order = Order([(1000, 2), (500, 1)])
        self.assertEqual(order.apply_discount(0.2), 2000)

    def test_zero_discount(self):
        order = Order([(1000, 2), (500, 1)])
        self.assertEqual(order.apply_discount(0), 2500)

    def test_discount_out_of_range(self):
        order = Order([(1000, 2)])
        with self.assertRaises(ValueError):
            order.apply_discount(0.6)
        with self.assertRaises(ValueError):
            order.apply_discount(-0.1)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOrder)
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("Все тесты прошли" if result.wasSuccessful() else "Есть упавшие тесты")
