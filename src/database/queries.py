import sys
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_REPEATABLE_READ, ISOLATION_LEVEL_SERIALIZABLE
from connection import get_connection


def _setup_import_paths():
    """Добавляет src и src/models в sys.path для запуска файла из любой оболочки."""
    src_root = Path(__file__).resolve().parent.parent
    for path in (src_root / "models", src_root):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)

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
        results = cursor.fetchall()
        cursor.close()
        return results
    

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

def create_order(user_id, product_id, quantity, total):
    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                 # Операция 1: Создать заказ
                cur.execute(
                    "INSERT INTO orders (user_id, total) VALUES (%s, %s) RETURNING id",
                    (user_id, total)
                    )
                order_id = cur.fetchone()[0]

                # Операция 2: Уменьшить количество товаров
                cur.execute(
                    "UPDATE products SET quantity = quantity - %s WHERE id = %s",
                    (quantity, product_id)
                    )

                # Проверка: количество товаров не отрицательное
                cur.execute("SELECT quantity FROM products WHERE id = %s", (product_id,))
                result = cur.fetchone()
                if result[0] < 0:
                    raise ValueError("Недостаточно товара на складе")

                # Все операции успешны - транзакция подтверждается автоматически
                return order_id
        except (psycopg2.Error, ValueError) as e:
            conn.rollback()
            print(f"Ошибка при создании заказа: {e}")
            raise

# # Тестирование
# try:
#     order_id = create_order(user_id=1, product_id=5, quantity=2, total=2000)
#     print(f"Заказ создан: {order_id}")
# except ValueError as e:
#     print(f"Ошибка: {e}")    


def transfer_money(from_id, to_id, amount):
    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT balance FROM users WHERE id = %s", (from_id,))
                result = cur.fetchone()[0]
                if result[0] < amount:
                    raise ValueError("Недостаточно средств")
                cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, from_id))
                cur.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, to_id))
                cur.execute("SELECT balance FROM users WHERE id = %s", (from_id,))
                result = cur.fetchone()
                if result[0] < 0:
                    raise ValueError("Недостаточно средств")
                conn.commit()
        except (psycopg2.Error, ValueError) as e:
            conn.rollback()
            print(f"Ошибка при переводе денег: {e}")
            raise

# # Тестирование
# try:
#     transfer_money(from_user_id=1, to_user_id=2, amount=500)
#     print("Перевод выполнен успешно")
# except ValueError as e:
#     print(f"Ошибка: {e}")


def generate_sales_report(start_date):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COALESCE(SUM(total), 0) FROM orders WHERE created_at >= %s",
                    (start_date,)
                    )
                total = cur.fetchone()[0]

                # Второе чтение: количество заказов
                # Благодаря REPEATABLE READ данные не изменятся между чтениями
                cur.execute(
                    "SELECT COUNT(*) FROM orders WHERE created_at >= %s",
                    (start_date,)
                    )
                count = cur.fetchone()[0]

                # Данные согласованы благодаря уровню изоляции
                return {
                    "total": float(total),
                    "count": count,
                    "average": float(total) / count if count > 0 else 0
                    }
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка при генерации отчета о продажах: {e}")
            raise


# Тестирование
# from datetime import datetime, timedelta

# start_date = datetime.now() - timedelta(days=30)
# report = generate_sales_report(start_date)
# print(f"Отчет: {report}")


def read_user_balance(user_id):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
                result = cur.fetchone()
                return result[0]
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка при чтении баланса пользователя: {e}")
            raise
        

def calculate_total_revenue(start_date, end_date):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        try:
            # Множественные чтения должны быть согласованными
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COALESCE(SUM(total), 0) FROM orders WHERE created_at BETWEEN %s AND %s",
                    (start_date, end_date)
                )
                total = cur.fetchone()[0]
                
                cur.execute(
                    "SELECT COUNT(*) FROM orders WHERE created_at BETWEEN %s AND %s",
                    (start_date, end_date)
                )
                count = cur.fetchone()[0]
                
                return {
                    "total": float(total),
                    "count": count,
                    "average": float(total) / count if count > 0 else 0
                }
        except psycopg2.Error as e:
            conn.rollback()
            
            raise

def critical_financial_operation(from_user_id, to_user_id, amount):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_SERIALIZABLE)
        try:
            with conn.cursor() as cur:
                # Проверка баланса
                cur.execute("SELECT balance FROM users WHERE id = %s", (from_user_id,))
                row = cur.fetchone()
                if row is None:
                    raise ValueError("Пользователь не найден")
                balance = row[0]
                
                if balance < amount:
                    raise ValueError("Недостаточно средств")
                
                # Списание
                cur.execute(
                    "UPDATE users SET balance = balance - %s WHERE id = %s",
                    (amount, from_user_id)
                )
                
                # Зачисление
                cur.execute(
                    "UPDATE users SET balance = balance + %s WHERE id = %s",
                    (amount, to_user_id)
                )
                return True
        except psycopg2.Error as e:
            conn.rollback()
 
            raise


# Тестирование
from datetime import datetime, timedelta

try:
    critical_financial_operation(from_user_id=1, to_user_id=2, amount=500)
    print("Операция выполнена успешно")
except ValueError as e:
    print(f"Ошибка: {e}")

try:
    calculate_total_revenue(start_date=datetime.now() - timedelta(days=30), end_date=datetime.now())
    print("Операция выполнена успешно")
except ValueError as e:
    print(f"Ошибка: {e}")

try:
    generate_sales_report(start_date=datetime.now() - timedelta(days=30))
    print("Операция выполнена успешно")
except ValueError as e:
    print(f"Ошибка: {e}")