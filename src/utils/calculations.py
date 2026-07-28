# Файл src/utils/calculations.py
def calculate_discount(price, discount_rate):
    return price * discount_rate

def calculate_delivery(weight, base_cost=100):
    return base_cost + weight * 10

def calculate_final_price(price, discount, delivery):
    return price - discount + delivery

#самостоятельные задания
import time
import functools
from typing import Iterator, Optional



# --- Переиспользуемый декоратор для замера производительности ---


def measure_time(func):
    """Декоратор: замеряет и выводит время выполнения функции"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} выполнена за {elapsed:.4f} сек")
        return result
    return wrapper


# --- Генератор для потоковой обработки заказов ---


def order_items_gen(orders: list) -> Iterator[float]:
    """Генератор: отдаёт стоимость каждого товара по одному"""
    for order in orders:
        for item in order.items:
            yield item.price * item.quantity


# --- Оптимизированная функция с аннотациями типов ---

@measure_time
def calculate_total_orders(orders: list) -> float:
    """Оптимизированный подход: генератор + sum + декоратор + type hints"""
    return sum(order_items_gen(orders))

# Исходная функция (медленная) — O(N * M)
# каждый раз обходит все items во всех заказах

@measure_time
def calculate_total_orders_slow(orders):
    """Медленный подход: обходит все item'ы каждого заказа"""
    total = 0
    for order in orders:
        for item in order.items:
            total += item.price * item.quantity
    return total

# Оптимизированная функция (быстрая) — O(N)
# использует предвычисленный order.total

class Item:
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity


class Order:
    def __init__(self, items):
        self.items = items
        # Предвычисляем сумму один раз при создании заказа —
        # это и есть источник реального ускорения
        self.total = sum(it.price * it.quantity for it in items)


# Пример использования
if __name__ == "__main__":
    orders = [
        Order([Item(1000, 2), Item(2000, 1)]),
        Order([Item(1500, 3), Item(500, 5)]),
        Order([Item(3000, 1)])
    ] * 1000  # Увеличиваем количество для измерения

    calculate_total_orders(orders)
    calculate_total_orders_slow(orders)

products = [
    {"name": "Ноутбук", "price": 50000},
    {"name": "Мышь", "price": 1500},
    {"name": "Монитор", "price": 25000},
    {"name": "Клавиатура", "price": 3000},
    {"name": "Наушники", "price": 8000}
    ]
    

# Только товары дороже 5000
expensive = list(filter(lambda p: p["price"] > 5000, products))
for product in expensive:
    print(f" {product['name']}: {product['price']} руб.")
print(f"Дорогих товаров: {sum(product['price'] for product in expensive)}")

def log_call(func):
    """Декоратор: логирует вызов функции с аргументами"""

    def wrapper(*args, **kwargs):
        args_str = ", ".join(str(a) for a in args)
        print(f"Вызов: {func.__name__}({args_str})")
        result = func(*args, **kwargs)
        return result
    return wrapper

@log_call
def calculate_order(price, quantity, discount):
    """Рассчитать стоимость заказа со скидкой"""
    return price * quantity * (1 - discount)

# Используем функцию - декоратор автоматически логирует вызовы
result_1 = calculate_order(1000, 3, 0.1)
result_2 = calculate_order(2000, 1, 0.2)

print(f"Заказ 1: {result_1} руб.")
print(f"Заказ 2: {result_2} руб.")

from typing import Optional


def calculate_discount(price: float, percent: float) -> float:
    return price * (1 - percent / 100)


def find_product(products: list[dict], product_id: int) -> Optional[dict]:
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def get_product_names(products: list[dict]) -> list[str]:
    names = []
    for product in products:
        names.append(product["name"])
    return names

# Проверка
products = [
    {"id": 1, "name": "Ноутбук", "price": 50000},
    {"id": 2, "name": "Мышь", "price": 1500}
    ]

print(calculate_discount(1000.0, 10.0)) # 900.0
print(find_product(products, 1)) # {'id': 1, 'name': 'Ноутбук', 'price': 50000}
print(find_product(products, 99)) # None
print(get_product_names(products)) # ['Ноутбук', 'Мышь']

#задание на проверку


class ProductSearchItem:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price


def find_product_in_list(products, product_id):
    """Поиск в списке (медленный)"""
    for product in products:
        if product.id == product_id:
            return product
    return None


def find_product_in_dict(products_dict, product_id):
    """Поиск в словаре (быстрый)"""
    return products_dict.get(product_id)


# Список от 1000 товаров
products = [
    ProductSearchItem(i, f"Товар {i}", 1000 + i)
    for i in range(1, 1001)
]

# Индекс: генератор словаря
products_dict = {product.id: product for product in products}

# Ищем последний элемент — худший случай для списка
search_id = 1000
iterations = 10_000

start = time.time()
result_list = None
for _ in range(iterations):
    result_list = find_product_in_list(products, search_id)
time_list = time.time() - start

start = time.time()
result_dict = None
for _ in range(iterations):
    result_dict = find_product_in_dict(products_dict, search_id)
time_dict = time.time() - start

speedup = time_list / time_dict if time_dict > 0 else float("inf")

print(f"Результат списка: {result_list.name if result_list else None}")
print(f"Результат словаря: {result_dict.name if result_dict else None}")
print(f"Результаты совпадают: {result_list is result_dict}")
print(f"Время поиска в списке: {time_list:.6f} сек")
print(f"Время поиска в словаре: {time_dict:.6f} сек")
print(f"Ускорение: {speedup:.2f}")