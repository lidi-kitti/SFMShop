# Файл src/database/queries.py
import psycopg2
from psycopg2 import Error
from connection import connect_to_db

def get_orders_with_products(conn, user_id):
    """Получить заказы пользователя с товарами"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
 orders.id as order_id,
 products.name as product_name,
 order_items.quantity,
products.price
FROM orders
INNER JOIN order_items ON orders.id = order_items.order_id
INNER JOIN products ON order_items.product_id = products.id
WHERE orders.user_id = %s""",
            (user_id,)
        )
        res = cursor.fetchall()
        cursor.close()
        return res
    except Error as e:
        print(f"Ошибка при получении заказов: {e}")
        return []

def get_order_statistics(conn):
    """Получает статистику по пользователям (количество заказов, общая сумма)"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, COUNT(*) as order_count, SUM(total) as total_sum
        FROM orders
        GROUP BY user_id
        ORDER BY total_sum DESC
        """)
    results = cursor.fetchall()
    cursor.close()
    return results

def get_user_order_history(conn, user_id):
    """Получает историю заказов пользователя с информацией о товарах"""
    cursor = conn.cursor()
    cursor.execute("""SELECT
 orders.id as order_id,
 products.name as product_name,
 order_items.quantity,
 products.price,
 orders.created_at
FROM orders
INNER JOIN order_items ON orders.id = order_items.order_id
INNER JOIN products ON order_items.product_id = products.id
WHERE orders.user_id = %s ORDER BY created_at DESC""",(user_id,)
        )
    results = cursor.fetchall()
    cursor.close()
    return results

def get_top_products(conn, limit=5):
    """Получает топ товаров по количеству продаж"""
    cursor = conn.cursor()
    cursor.execute("""
            SELECT 
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

def main():

    connection = connect_to_db()
    try:
       print(get_orders_with_products(connection, 1))
       print(get_order_statistics(connection))
       print(get_top_products(connection))
       print(get_user_order_history(connection,1))
    except Exception as e:
        print("Ошибка: ", e)
    finally:
        connection.close()

if __name__ == "__main__":
    main()