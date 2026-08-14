import psycopg2


def get_order_statistics(conn):
    """Получить статистику по заказам пользователей"""
    try:
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
    except psycopg2.Error as e:
        print(f"Ошибка при получении статистики: {e}")
        return []


def get_user_order_history(conn, user_id):
    """Получить историю заказов пользователя с информацией о товарах"""
    try:
        cursor = conn.cursor()
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
    except psycopg2.Error as e:
        print(f"Ошибка при получении истории заказов: {e}")
        return []


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
