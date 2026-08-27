# Создай отдельный файл scripts/orders_normalized.py
import sqlite3


def build_schema(conn: sqlite3.Connection) -> None:
    # Создай нормализованные таблицы: users, products, orders, order_items.
    # order_items связывает заказ и товар, хранит только quantity (не цену!).
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.execute("""
    """)
    conn.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    conn.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    if conn.execute("SELECT name FROM sqlite_master WHERE name = 'order_items'").fetchone() is None:
        conn.execute("""
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )   
        """)
    else:
        print("Table order_items already exists")


def main() -> None:
    conn = sqlite3.connect(":memory:")
    build_schema(conn)
    # заполни данными и посчитай сумму каждого заказа через JOIN
    conn.execute("""
        INSERT INTO users (name, email) VALUES ('John Doe', 'john.doe@example.com')
    """)
    conn.execute("""
        INSERT INTO products (name, price) VALUES ('Product 1', 100.00)
    """)
    conn.execute("""
        INSERT INTO orders (user_id) VALUES (1)
    """)
    conn.execute("""
        INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 1, 1)
    """)
    result = conn.execute("""
        SELECT orders.id, SUM(products.price * order_items.quantity) AS total_price
        FROM orders
        JOIN order_items ON orders.id = order_items.order_id
        JOIN products ON order_items.product_id = products.id
        GROUP BY orders.id
    """)
    print(result.fetchall())
    conn.close()


if __name__ == "__main__":
    main()