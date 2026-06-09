# Файл src/database/connection.py
import os
import psycopg2
from psycopg2 import Error

def connect_to_db():
    # Подключение к БД возвращает соединение
    try:
        return psycopg2.connect(
            host="localhost",
            database="sfmshop",
            user="postgres",
            password=os.environ.get("DB_PASSWORD", "user")
        )
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

def add_product(conn, name, price, quantity):
    #добавляет товар
    # Создание курсора
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
        (name, price, quantity)
    )

    # Сохранить изменения
    conn.commit()
    cursor.close()
    print(f"Товар добавлен: {name}, {price}, {quantity}")


def get_all_products(conn):
    #возврает все товары
    # Создание курсора
    cursor = conn.cursor()

    # Выполнение запроса
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return products

def get_product_by_id(conn, product_id):
    """Получить товар по ID"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        return product
    except Error as e:
        print(f"Ошибка при получении товара: {e}")
        return None

def update_product_price(conn, product_id, new_price):
    #обновляет цену
    # Создание курсора
    cursor = conn.cursor()

    # Выполнение запроса
    cursor.execute("UPDATE products SET price = %s WHERE id = %s",
    (new_price, product_id))
    # Сохранить изменения
    conn.commit()
    cursor.close()
    print(f"Цена обновлена: {new_price}")

def update_product(conn, product_id, new_data):
    """Обновить товар"""
    try:
        existing = get_product_by_id(conn, product_id)
        if not existing:
            return None

        name = new_data.get("name", existing[1])
        price = new_data.get("price", existing[2])
        quantity = new_data.get("quantity", existing[3])

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET name = %s, price = %s, quantity = %s WHERE id = %s",
            (name, price, quantity, product_id),
        )
        conn.commit()
        cursor.close()
        return get_product_by_id(conn, product_id)
    except Error as e:
        print(f"Ошибка при обновлении товара: {e}")
        return None

def delete_product(conn, product_id):
    """Удалить товар"""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        deleted = cursor.rowcount
        conn.commit()
        cursor.close()
        return deleted
    except Error as e:
        print(f"Ошибка при удалении товара: {e}")
        return 0
def create_user(conn, name, email):
    """Создать пользователя"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        conn.commit()
        cursor.close()
        print(f"Пользователь создан: {name}, {email}")
    except Error as e:
        print(f"Ошибка при создании пользователя: {e}")


def get_user_by_id(conn, user_id):
    """Получить пользователя по ID"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2]
            }
        return None
    except Error as e:
        print(f"Ошибка при получении пользователя: {e}")
        return None

def create_order(conn, user_id, total):
    """Создать заказ"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (user_id, total) VALUES (%s, %s) RETURNING id",
            (user_id, total),
        )
        order_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        print(f"Заказ создан: user_id={user_id}, total={total}")
        return order_id
    except Error as e:
        print(f"Ошибка при создании заказа: {e}")
        return None

def delete_order(conn, order_id):
    """Удалить заказ"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM orders WHERE id =%s",
            (order_id)
        )
        deleted = cursor.rowcount
        conn.commit()
        cursor.close()
        print(f"Заказ order_id = {order_id} удален")
        return deleted
    except Error as e:
        print(f"Ошибка при удалении заказа: {e}")


def get_user_orders(conn, user_id):
    """Получить заказы пользователя"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders WHERE user_id = %s",
            (user_id,)
        )
        orders = cursor.fetchall()
        cursor.close()
        return orders
    except Error as e:
        print(f"Ошибка при получении заказов: {e}")
        return []

