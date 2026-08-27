# ==================
# УРОК 45: Индексы в PostgreSQL
# ==================

# Практика: Задание 2 - Проверь, что индекс используется (sqlite3)
import sqlite3


def plan_uses_index(conn, sql, params):
    """Верни True, если в плане запроса встречается 'USING INDEX'."""
    rows = conn.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    detail = " ".join(str(r[-1]) for r in rows)
    return "USING INDEX" in detail


def main():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    # создай таблицу products, наполни её и проверь план до/после индекса
    cur.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER)")
    products = [
        (1, "Ноутбук", 75000),
        (2, "Мышь", 1200),
        (3, "Клавиатура", 3500),
        (4, "Монитор", 22000),
        (5, "Веб-камера", 4800),
    ]
    conn.executemany("INSERT INTO products VALUES (?, ?, ?)", products)

    query = "SELECT id, price FROM products WHERE name = ?"

    # До создания индекса — поиск идёт полным сканированием таблицы
    print("До индекса, использует индекс:", plan_uses_index(conn, query, ("Монитор",)))

    # Создаём индекс на столбце name
    conn.execute("CREATE INDEX idx_products_name ON products(name)")

    # После создания индекса — поиск идёт через индекс
    print("После индекса, использует индекс:", plan_uses_index(conn, query, ("Монитор",)))

    # Сам результат запроса не меняется — меняется только способ поиска
    row = conn.execute(query, ("Монитор",)).fetchone()
    print(f"Найден товар id={row[0]}, цена={row[1]}")

    conn.close()
    
if __name__ == "__main__":
    main()    