"""Замер производительности: до и после оптимизации каталога и сумм заказов."""
from __future__ import annotations

import time
from types import SimpleNamespace


def calculate_total_orders_slow(orders: list) -> float:
    total = 0
    for order in orders:
        for item in order.items:
            total += item.price * item.quantity
    return total


def calculate_total_orders_fast(orders: list) -> float:
    return sum(order.total for order in orders)


def find_product_in_list(products: list, product_id: int):
    for product in products:
        if product.id == product_id:
            return product
    return None


def find_product_in_dict(index: dict, product_id: int):
    return index.get(product_id)


def _sample_orders(n_orders: int = 2000, n_items: int = 8) -> list:
    orders = []
    for i in range(n_orders):
        items = [
            SimpleNamespace(price=100.0 + j, quantity=2)
            for j in range(n_items)
        ]
        total = sum(item.price * item.quantity for item in items)
        orders.append(SimpleNamespace(items=items, total=total))
    return orders


def _sample_products(n: int = 20_000) -> list:
    return [SimpleNamespace(id=i, name=f"p{i}") for i in range(1, n + 1)]


def main() -> None:
    orders = _sample_orders()
    products = _sample_products()
    target_id = products[-1].id

    start = time.perf_counter()
    slow_total = calculate_total_orders_slow(orders)
    time_slow = time.perf_counter() - start

    start = time.perf_counter()
    fast_total = calculate_total_orders_fast(orders)
    time_fast = time.perf_counter() - start

    start = time.perf_counter()
    found_list = find_product_in_list(products, target_id)
    time_list = time.perf_counter() - start

    index = {p.id: p for p in products}
    start = time.perf_counter()
    found_dict = find_product_in_dict(index, target_id)
    time_dict = time.perf_counter() - start

    print("=== Сумма заказов ===")
    print(f"До (обход items):     {time_slow:.6f} с  результат={slow_total}")
    print(f"После (order.total):  {time_fast:.6f} с  результат={fast_total}")
    print(f"Совпадают: {slow_total == fast_total}")
    if time_fast > 0:
        print(f"Ускорение: {time_slow / time_fast:.1f}x")

    print("=== Поиск товара ===")
    print(f"До (список O(n)):     {time_list:.6f} с")
    print(f"После (словарь O(1)): {time_dict:.6f} с")
    print(f"Совпадают: {found_list is found_dict}")
    if time_dict > 0:
        print(f"Ускорение поиска: {time_list / time_dict:.1f}x")


if __name__ == "__main__":
    main()
