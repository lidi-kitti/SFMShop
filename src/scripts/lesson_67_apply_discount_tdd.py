# Создай файл scripts/lesson_67_apply_discount_tdd.py
import io
import unittest


def apply_discount(price: float, quantity: int) -> float:
    """Итоговая стоимость со скидкой за количество в SFMShop."""
    total = float(price * quantity)
    if quantity >= 6:
        return total * 0.9
    if quantity >= 3:
        return total * 0.95
    return total


class TestApplyDiscount(unittest.TestCase):
    def test_no_discount(self):
        # меньше 3 шт -> скидки нет
        self.assertEqual(apply_discount(100, 2), 200.0)
        self.assertEqual(apply_discount(100, 1), 100.0)

    def test_five_percent(self):
        self.assertEqual(apply_discount(100, 3), 285.0)
        self.assertEqual(apply_discount(100, 4), 380.0)
        self.assertEqual(apply_discount(100, 5), 475.0)

    def test_ten_percent(self):
        self.assertEqual(apply_discount(100, 6), 540.0)
        self.assertEqual(apply_discount(100, 10), 900.0)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApplyDiscount)
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("Все тесты прошли" if result.wasSuccessful() else "Есть упавшие тесты")
    print(f"apply_discount(100, 2) = {apply_discount(100, 2)}")
    print(f"apply_discount(100, 4) = {apply_discount(100, 4)}")
    print(f"apply_discount(100, 10) = {apply_discount(100, 10)}")
