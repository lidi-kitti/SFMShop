import os
from contextlib import contextmanager

import psycopg2
from psycopg2 import Error


def connect_to_db():
    """Подключение к базе данных PostgreSQL"""
    return psycopg2.connect(
        host="localhost",
        database="sfmshop",
        user="postgres",
        password=os.environ.get("DB_PASSWORD", "password")
        )


@contextmanager
def get_connection():
    """Контекстный менеджер соединения: commit при успехе, rollback при ошибке."""
    conn = connect_to_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def add_product(conn, name, price, quantity):
    """Добавить товар в базу данных"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
        (name, price, quantity)
        )
    conn.commit()
    cursor.close()
    print(f"Товар добавлен: {name}, {price}, {quantity}")


def get_all_products(conn):
    """Получить все товары из базы данных"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return products


def update_product_price(conn, product_id, new_price):
    """Обновить цену товара"""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET price = %s WHERE id = %s",
        (new_price, product_id)
        )
    conn.commit()
    cursor.close()
    print(f"Цена обновлена: {new_price}")


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
            "INSERT INTO orders (user_id, total) VALUES (%s, %s)",
            (user_id, total)
        )
        conn.commit()
        cursor.close()
        print(f"Заказ создан: user_id={user_id}, total={total}")
    except Error as e:
        print(f"Ошибка при создании заказа: {e}")


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


def main():
    # Подключение к БД
    conn = connect_to_db()

    try:
        # Добавить товар
        add_product(conn, "Ноутбук", 50000.00, 10)

        # Получить все товары
        products = get_all_products(conn)
        print("Все товары:")
        for product in products:
            print(product)

        # Обновить цену
        update_product_price(conn, 1, 45000.00)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
