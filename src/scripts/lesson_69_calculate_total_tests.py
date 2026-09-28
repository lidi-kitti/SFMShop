# Создай файл scripts/lesson_69_calculate_total_tests.py
import io
import unittest


def calculate_total(price, quantity, discount_rate):
    """Итоговая стоимость позиции заказа SFMShop с учётом скидки."""
    # price, quantity >= 0; discount_rate в диапазоне 0..1
    # верни округлённую до 2 знаков сумму
    if price < 0 or quantity < 0:
        raise ValueError("Цена и количество не могут быть отрицательными")
    if not 0 <= discount_rate <= 1:
        raise ValueError("Скидка должна быть в диапазоне 0..1")
    return round(price * quantity * (1 - discount_rate), 2)


class TestCalculateTotal(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(calculate_total(100, 2, 0), 200.0)
        self.assertEqual(calculate_total(50.5, 1, 0), 50.5)

    def test_with_discount(self):
        self.assertEqual(calculate_total(100, 2, 0.1), 180.0)
        self.assertEqual(calculate_total(200, 3, 1), 0.0)

    def test_rounding(self):
        self.assertEqual(calculate_total(10.125, 2, 0), 20.25)
        self.assertEqual(calculate_total(99.999, 1, 0), 100.0)

    def test_invalid_args(self):
        with self.assertRaises(ValueError):
            calculate_total(-1, 1, 0)
        with self.assertRaises(ValueError):
            calculate_total(10, -2, 0)
        with self.assertRaises(ValueError):
            calculate_total(10, 1, 1.5)


def main():
    # загрузи тесты из TestCalculateTotal, запусти их через TextTestRunner
    # и выведи сводку по result.testsRun / failures / errors / wasSuccessful()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculateTotal)
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("Все тесты прошли" if result.wasSuccessful() else "Есть упавшие тесты")


if __name__ == "__main__":
    main()
