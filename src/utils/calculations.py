# Файл src/utils/calculations.py
import time


def calculate_discount(price, discount_rate):
    return price * discount_rate


def calculate_total(price, quantity):
    return price * quantity


# --- Оптимизация обработки заказов: замер производительности ---
# Исходная функция (медленная) — O(N * M)
# каждый раз обходит все items во всех заказах


def calculate_total_orders_slow(orders):
    """Медленный подход: обходит все item'ы каждого заказа"""
    total = 0
    for order in orders:
        for item in order.items:
            total += item.price * item.quantity
    return total


# Оптимизированная функция (быстрая) — O(N)
# использует предвычисленный order.total


def calculate_total_orders(orders):
    """Быстрый подход: сумма по предвычисленным order.total"""
    return sum(order.total for order in orders)


def benchmark_calculate_total(orders):
    """Измерить производительность обеих функций"""
    # Медленная версия
    start_time = time.time()
    result_slow = calculate_total_orders_slow(orders)
    time_slow = time.time() - start_time

    # Быстрая версия
    start_time = time.time()
    result_fast = calculate_total_orders(orders)
    time_fast = time.time() - start_time

    # Сравнение
    speedup = time_slow / time_fast if time_fast > 0 else 0

    print(f"Медленная версия: {time_slow:.4f} секунд")
    print(f"Быстрая версия: {time_fast:.4f} секунд")
    print(f"Ускорение: {speedup:.2f}x")
    print(f"Результаты совпадают: {result_slow == result_fast}")

    return {
        "time_slow": time_slow,
        "time_fast": time_fast,
        "speedup": speedup,
        "result": result_fast,
    }


# --- Поиск по словарю-индексу: список (O(n)) vs словарь (O(1)) ---


def find_product_in_list(products, product_id):
    """Поиск в списке (медленный, O(n))"""
    for product in products:
        if product.id == product_id:
            return product
    return None


def create_products_index(products):
    """Создать словарь для быстрого поиска (O(1))"""
    return {product.id: product for product in products}


def find_product_in_dict(products_dict, product_id):
    """Поиск в словаре (быстрый, O(1))"""
    return products_dict.get(product_id)


def benchmark_search(products, product_id):
    """Измерить производительность поиска в списке vs словаре"""
    # Поиск в списке
    start_time = time.time()
    result_list = find_product_in_list(products, product_id)
    time_list = time.time() - start_time

    # Создание индекса
    start_time = time.time()
    products_dict = create_products_index(products)
    time_index = time.time() - start_time

    # Поиск в словаре
    start_time = time.time()
    result_dict = find_product_in_dict(products_dict, product_id)
    time_dict = time.time() - start_time

    # Общее время для словаря (создание + поиск)
    time_dict_total = time_index + time_dict

    # Сравнение
    speedup = time_list / time_dict if time_dict > 0 else 0

    print(f"Поиск в списке: {time_list:.6f} секунд")
    print(f"Создание индекса: {time_index:.6f} секунд")
    print(f"Поиск в словаре: {time_dict:.6f} секунд")
    print(f"Общее время (словарь): {time_dict_total:.6f} секунд")
    print(f"Ускорение поиска: {speedup:.2f}x")
    print(f"Результаты совпадают: {result_list == result_dict}")

    return {
        "time_list": time_list,
        "time_dict": time_dict,
        "time_index": time_index,
        "speedup": speedup,
        "result": result_dict,
    }
