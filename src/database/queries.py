import sys
from pathlib import Path

import psycopg2
from psycopg2.extensions import (
    ISOLATION_LEVEL_READ_COMMITTED,
    ISOLATION_LEVEL_REPEATABLE_READ,
    ISOLATION_LEVEL_SERIALIZABLE,
)


def _setup_import_paths():
    """Добавляет src, src/models и src/database в sys.path для запуска файла из любой оболочки."""
    src_root = Path(__file__).resolve().parent.parent
    db_dir = Path(__file__).resolve().parent
    for path in (src_root / "models", src_root, db_dir):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


_setup_import_paths()
from connection import get_connection

_MAX_SERIALIZATION_RETRIES = 3


def _run_serializable(work):
    """I: SERIALIZABLE и повтор при конфликте сериализации / deadlock."""
    last_error = None
    for _ in range(_MAX_SERIALIZATION_RETRIES):
        try:
            with get_connection() as conn:
                conn.set_isolation_level(ISOLATION_LEVEL_SERIALIZABLE)
                return work(conn)
        except (psycopg2.errors.SerializationFailure, psycopg2.errors.DeadlockDetected) as exc:
            last_error = exc
    raise last_error


def _require_row(row, message):
    if row is None:
        raise ValueError(message)
    return row


def get_order_statistics():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, COUNT(*) as order_count, SUM(total) as total_sum
                FROM orders
                GROUP BY user_id
                ORDER BY total_sum DESC
            """)
            return cursor.fetchall()


def get_user_order_history(user_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT
                orders.id as order_id,
                orders.created_at,
                products.name as product_name,
                order_items.quantity,
                products.price
            FROM orders
            INNER JOIN order_items ON orders.id = order_items.order_id
            INNER JOIN products ON order_items.product_id = products.id
            WHERE orders.user_id = %s
            ORDER BY orders.created_at DESC
        """, (user_id,))
            return cursor.fetchall()


def get_top_products(conn, limit=5):
    """Получить топ товаров по количеству продаж"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                products.id,
                products.name,
                SUM(order_items.quantity) as total_sold
            FROM products
            INNER JOIN order_items ON products.id = order_items.product_id
            GROUP BY products.id, products.name
            ORDER BY total_sold DESC
            LIMIT %s
        """, (limit,))
        results = cursor.fetchall()
        cursor.close()
        return results
    except psycopg2.Error as e:
        print(f"Ошибка при получении топ товаров: {e}")
        return []


def get_orders_with_products(conn, user_id):
    """Получить заказы пользователя с товарами"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                orders.id,
                products.name,
                order_items.quantity,
                products.price
            FROM orders
            INNER JOIN order_items ON orders.id = order_items.order_id
            INNER JOIN products ON order_items.product_id = products.id
            WHERE orders.user_id = %s
        """, (user_id,))
        results = cursor.fetchall()
        cursor.close()
        return results
    except psycopg2.Error as e:
        print(f"Ошибка при получении заказов с товарами: {e}")
        return []


def create_order(user_id, product_id, quantity, total=None):
    """A: заказ, позиция и склад в одной транзакции. C/I: FOR UPDATE и условный UPDATE."""
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным")

    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT price, quantity FROM products WHERE id = %s FOR UPDATE",
                    (product_id,),
                )
                price, stock = _require_row(cur.fetchone(), "Товар не найден")
                if stock < quantity:
                    raise ValueError("Недостаточно товара на складе")

                order_total = price * quantity if total is None else total
                cur.execute(
                    "INSERT INTO orders (user_id, total) VALUES (%s, %s) RETURNING id",
                    (user_id, order_total),
                )
                order_id = cur.fetchone()[0]
                cur.execute(
                    """INSERT INTO order_items (order_id, product_id, quantity, price)
                       VALUES (%s, %s, %s, %s)""",
                    (order_id, product_id, quantity, price),
                )
                cur.execute(
                    """UPDATE products SET quantity = quantity - %s
                       WHERE id = %s AND quantity >= %s""",
                    (quantity, product_id, quantity),
                )
                if cur.rowcount != 1:
                    raise ValueError("Недостаточно товара на складе")
                return order_id
        except (psycopg2.Error, ValueError) as e:
            print(f"Ошибка при создании заказа: {e}")
            raise


def _transfer_money_tx(conn, from_id, to_id, amount):
    if from_id == to_id:
        raise ValueError("Нельзя перевести средства самому себе")
    if amount <= 0:
        raise ValueError("Сумма перевода должна быть положительной")

    with conn.cursor() as cur:
        first_id, second_id = (from_id, to_id) if from_id < to_id else (to_id, from_id)
        cur.execute("SELECT id, balance FROM users WHERE id = %s FOR UPDATE", (first_id,))
        first = _require_row(cur.fetchone(), "Пользователь не найден")
        cur.execute("SELECT id, balance FROM users WHERE id = %s FOR UPDATE", (second_id,))
        second = _require_row(cur.fetchone(), "Пользователь не найден")
        balances = {first[0]: first[1], second[0]: second[1]}
        if balances[from_id] < amount:
            raise ValueError("Недостаточно средств")

        cur.execute(
            "UPDATE users SET balance = balance - %s WHERE id = %s AND balance >= %s",
            (amount, from_id, amount),
        )
        if cur.rowcount != 1:
            raise ValueError("Недостаточно средств")
        cur.execute(
            "UPDATE users SET balance = balance + %s WHERE id = %s",
            (amount, to_id),
        )
        if cur.rowcount != 1:
            raise ValueError("Получатель не найден")
    return True


def transfer_money(from_id, to_id, amount):
    try:
        return _run_serializable(lambda conn: _transfer_money_tx(conn, from_id, to_id, amount))
    except (psycopg2.Error, ValueError) as e:
        print(f"Ошибка при переводе денег: {e}")
        raise


def generate_sales_report(start_date):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT COALESCE(SUM(total), 0), COUNT(*)
                       FROM orders WHERE created_at >= %s""",
                    (start_date,),
                )
                total, count = cur.fetchone()
                return {
                    "total": float(total),
                    "count": count,
                    "average": float(total) / count if count > 0 else 0,
                }
        except psycopg2.Error as e:
            print(f"Ошибка при генерации отчета о продажах: {e}")
            raise


def read_user_balance(user_id):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
                result = _require_row(cur.fetchone(), "Пользователь не найден")
                return result[0]
        except psycopg2.Error as e:
            print(f"Ошибка при чтении баланса пользователя: {e}")
            raise


def calculate_total_revenue(start_date, end_date):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT COALESCE(SUM(total), 0), COUNT(*)
                       FROM orders WHERE created_at BETWEEN %s AND %s""",
                    (start_date, end_date),
                )
                total, count = cur.fetchone()
                return {
                    "total": float(total),
                    "count": count,
                    "average": float(total) / count if count > 0 else 0,
                }
        except psycopg2.Error as e:
            raise


def critical_financial_operation(from_user_id, to_user_id, amount):
    return _run_serializable(
        lambda conn: _transfer_money_tx(conn, from_user_id, to_user_id, amount)
    )


def create_order_with_acid(user_id, product_id, quantity, total=None):
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным")

    def work(conn):
        with conn.cursor() as cur:
            # C + I: блокировка строк до изменений
            cur.execute("SELECT balance FROM users WHERE id = %s FOR UPDATE", (user_id,))
            balance = _require_row(cur.fetchone(), "Пользователь не найден")[0]
            cur.execute(
                "SELECT price, quantity FROM products WHERE id = %s FOR UPDATE",
                (product_id,),
            )
            price, stock = _require_row(cur.fetchone(), "Товар не найден")
            computed_total = price * quantity
            if total is not None and computed_total != total:
                raise ValueError("Сумма заказа не совпадает с ценой товара")
            if balance < computed_total:
                raise ValueError("Недостаточно средств")
            if stock < quantity:
                raise ValueError("Недостаточно товара на складе")

            # A: заказ, позиция, склад и баланс — одна транзакция
            cur.execute(
                "INSERT INTO orders (user_id, total) VALUES (%s, %s) RETURNING id",
                (user_id, computed_total),
            )
            order_id = cur.fetchone()[0]
            cur.execute(
                """INSERT INTO order_items (order_id, product_id, quantity, price)
                   VALUES (%s, %s, %s, %s)""",
                (order_id, product_id, quantity, price),
            )
            cur.execute(
                """UPDATE products SET quantity = quantity - %s
                   WHERE id = %s AND quantity >= %s""",
                (quantity, product_id, quantity),
            )
            if cur.rowcount != 1:
                raise ValueError("Недостаточно товара на складе")
            cur.execute(
                """UPDATE users SET balance = balance - %s
                   WHERE id = %s AND balance >= %s""",
                (computed_total, user_id, computed_total),
            )
            if cur.rowcount != 1:
                raise ValueError("Недостаточно средств")
            return order_id

    try:
        # I: SERIALIZABLE + retry; D: commit в get_connection()
        return _run_serializable(work)
    except (psycopg2.Error, ValueError) as e:
        print(f"Ошибка при создании заказа: {e}")
        raise

import time

def measure_index_performance():
    """Измерение производительности запросов с индексами"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Тест 1: Поиск товара по названию
            print("Тест 1: Поиск товара по названию")
            
            # Без индекса
            start_time = time.perf_counter()
            cur.execute("SELECT * FROM products WHERE name = %s", ("Ноутбук",))
            result = cur.fetchone()
            time_without_index = time.perf_counter() - start_time
            
            # Создание индекса
            cur.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)")
            conn.commit()
            
            # С индексом
            start_time = time.perf_counter()
            cur.execute("SELECT * FROM products WHERE name = %s", ("Ноутбук",))
            result = cur.fetchone()
            time_with_index = time.perf_counter() - start_time
            
            print(f"  Без индекса: {time_without_index:.6f} сек")
            print(f"  С индексом: {time_with_index:.6f} сек")
            if time_with_index > 0:
                speedup = time_without_index / time_with_index
                print(f"  Ускорение: {speedup:.2f}x")
            
            # Тест 2: Поиск заказов по пользователю
            print("\nТест 2: Поиск заказов по пользователю")
            
            # Без индекса
            start_time = time.perf_counter()
            cur.execute("SELECT * FROM orders WHERE user_id = %s", (1,))
            results = cur.fetchall()
            time_without_index = time.perf_counter() - start_time
            
            # Создание индекса
            cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
            conn.commit()
            
            # С индексом
            start_time = time.perf_counter()
            cur.execute("SELECT * FROM orders WHERE user_id = %s", (1,))
            results = cur.fetchall()
            time_with_index = time.perf_counter() - start_time
            
            print(f"  Без индекса: {time_without_index:.6f} сек")
            print(f"  С индексом: {time_with_index:.6f} сек")
            if time_with_index > 0:
                speedup = time_without_index / time_with_index
                print(f"  Ускорение: {speedup:.2f}x")

