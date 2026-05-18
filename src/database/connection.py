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
    connection = connect_to_db()
    try:
        add_product(connection, "Ноутбук", 50000.00, 10)

        all_products = get_all_products(connection)
        print("Все товары: ", all_products)
        for product in all_products:
            print(product)
            update_product_price(connection, 1, 45000.00)

        create_user(connection, "Иван", "ivan@test.ru")

        find_user = get_user_by_id(connection, 1)
        if find_user:
            print(f"Пользователь найден: {find_user}")

        create_order(connection, 1,  50000.00)

        user_order = get_user_orders(connection, 1)
        print(f"Заказы пользователя: {user_order}")
    except Exception as e:
        print("Ошибка: ", e)
    finally:
        connection.close()

if __name__ == "__main__":
    main()