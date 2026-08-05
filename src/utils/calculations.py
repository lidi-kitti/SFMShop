# Файл src/utils/calculations.py
"""Расчёты и оптимизации поиска/сортировки для SFMShop."""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any, Optional


# --- Базовые расчёты ---


def calculate_discount(price: float, discount_rate: float) -> float:
    """Скидка: price * rate (например, 0.1 = 10%)."""
    return price * discount_rate


def calculate_delivery(weight: float, base_cost: float = 100) -> float:
    return base_cost + weight * 10


def calculate_final_price(price: float, discount: float, delivery: float) -> float:
    return price - discount + delivery


# --- Вспомогательные модели для бенчмарков ---


class Product:
    def __init__(self, id: int, name: str, price: float):
        self.id = id
        self.name = name
        self.price = price


class Order:
    def __init__(self, id: int, created_at: datetime, total: float):
        self.id = id
        self.created_at = created_at
        self.total = total


# --- 1. Поиск: O(n) список → O(1) словарь ---


def find_product_in_list(products: list[Product], product_id: int) -> Optional[Product]:
    """Линейный поиск в списке: O(n)."""
    for product in products:
        if product.id == product_id:
            return product
    return None


def create_products_catalog(products: list[Product]) -> dict[int, Product]:
    """Словарь для быстрого поиска товаров по ID: O(n) построение, O(1) поиск."""
    return {product.id: product for product in products}


def find_product(products_index: dict[int, Product], product_id: int) -> Optional[Product]:
    """Поиск в словаре: O(1)."""
    return products_index.get(product_id)


# --- 2. Имена товаров: цикл + append → list comprehension ---


def get_product_names_slow(products: list[Product]) -> list[str]:
    """До оптимизации: цикл с append."""
    names = []
    for product in products:
        names.append(product.name)
    return names


def get_product_names(products: list[Product]) -> list[str]:
    """После оптимизации: генератор списка."""
    return [product.name for product in products]


# --- 3. Сумма цен: вложенный цикл → sum() ---


def sum_prices_slow(products: list[Product]) -> float:
    """До оптимизации: ручной цикл."""
    total = 0.0
    for product in products:
        total += product.price
    return total


def sum_prices(products: list[Product]) -> float:
    """После оптимизации: встроенный sum()."""
    return sum(product.price for product in products)


# --- 4. Сортировка: O(n²) ручная → O(n log n) sorted() ---


def sort_orders_manual(orders: list[Order]) -> list[Order]:
    """Ручная пузырьковая сортировка по created_at: O(n²)."""
    items = orders.copy()
    n = len(items)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if items[j].created_at > items[j + 1].created_at:
                items[j], items[j + 1] = items[j + 1], items[j]
                swapped = True
        if not swapped:
            break
    return items


def sort_orders(orders: list[Order]) -> list[Order]:
    """Встроенная сортировка: O(n log n)."""
    return sorted(orders, key=lambda x: x.created_at)


# --- Тестовые данные ---


def create_test_products(count: int = 1000) -> list[Product]:
    """Создать список тестовых товаров."""
    return [Product(i, f"Товар {i}", 1000 + i) for i in range(1, count + 1)]


def create_test_orders(count: int = 1000) -> list[Order]:
    """Создать список заказов с перемешанными датами."""
    base = datetime(2024, 1, 1)
    return [
        Order(i, base + timedelta(minutes=(i * 37) % count), 1000.0 + i)
        for i in range(1, count + 1)
    ]


def benchmark_search(products: list[Product], product_id: int) -> dict[str, float]:
    """Сравнить время поиска в списке vs словаре."""
    # Поиск в списке (много повторов, чтобы замер был стабильным)
    iterations = 5_000
    start_time = time.time()
    result_list = None
    for _ in range(iterations):
        result_list = find_product_in_list(products, product_id)
    time_list = time.time() - start_time

    # Поиск в словаре
    products_dict = create_products_catalog(products)
    start_time = time.time()
    result_dict = None
    for _ in range(iterations):
        result_dict = products_dict.get(product_id)
    time_dict = time.time() - start_time

    speedup = time_list / time_dict if time_dict > 0 else 0.0
    return {
        "time_list": time_list,
        "time_dict": time_dict,
        "speedup": speedup,
        "results_match": result_list is result_dict,
    }


def benchmark_optimizations() -> dict[str, dict[str, Any]]:
    """Измерить производительность оптимизированных функций."""
    results: dict[str, dict[str, Any]] = {}

    # --- Тест 1: поиск товара (O(n) → O(1)) ---
    products = create_test_products(1000)
    product_id = 1000  # худший случай для линейного поиска

    start_time = time.time()
    for _ in range(5_000):
        find_product_in_list(products, product_id)
    time_before = time.time() - start_time

    products_dict = create_products_catalog(products)
    start_time = time.time()
    for _ in range(5_000):
        find_product(products_dict, product_id)
    time_after = time.time() - start_time

    results["product_search"] = {
        "time_before": time_before,
        "time_after": time_after,
        "speedup": time_before / time_after if time_after > 0 else 0.0,
    }

    # --- Тест 2: имена товаров (append → comprehension) ---
    start_time = time.time()
    for _ in range(2_000):
        get_product_names_slow(products)
    time_before = time.time() - start_time

    start_time = time.time()
    for _ in range(2_000):
        get_product_names(products)
    time_after = time.time() - start_time

    results["product_names"] = {
        "time_before": time_before,
        "time_after": time_after,
        "speedup": time_before / time_after if time_after > 0 else 0.0,
    }

    # --- Тест 3: сумма цен (цикл → sum) ---
    start_time = time.time()
    for _ in range(2_000):
        sum_prices_slow(products)
    time_before = time.time() - start_time

    start_time = time.time()
    for _ in range(2_000):
        sum_prices(products)
    time_after = time.time() - start_time

    results["sum_prices"] = {
        "time_before": time_before,
        "time_after": time_after,
        "speedup": time_before / time_after if time_after > 0 else 0.0,
    }

    # --- Тест 4: сортировка заказов (O(n²) → O(n log n)) ---
    orders = create_test_orders(1000)

    start_time = time.time()
    sorted_manual = sort_orders_manual(orders)
    time_before = time.time() - start_time

    start_time = time.time()
    sorted_fast = sort_orders(orders)
    time_after = time.time() - start_time

    results["sort_orders"] = {
        "time_before": time_before,
        "time_after": time_after,
        "speedup": time_before / time_after if time_after > 0 else 0.0,
        "order_match": [o.id for o in sorted_manual] == [o.id for o in sorted_fast],
    }

    # Вывести результаты
    print("Результаты оптимизации:")
    for func_name, metrics in results.items():
        print(f"{func_name}:")
        print(f"  До: {metrics['time_before']:.6f} сек")
        print(f"  После: {metrics['time_after']:.6f} сек")
        print(f"  Ускорение: {metrics['speedup']:.2f}x")
        if "order_match" in metrics:
            print(f"  Порядок совпадает: {metrics['order_match']}")

    return results


if __name__ == "__main__":
    benchmark_optimizations()
