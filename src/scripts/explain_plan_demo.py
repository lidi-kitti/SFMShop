# Создай отдельный файл scripts/explain_plan_demo.py
import sqlite3


def plan_operation(cur, query, params):
    """Вернуть 'SCAN' или 'SEARCH' для таблицы orders из плана запроса."""
    cur.execute("EXPLAIN QUERY PLAN " + query, params)
    # пройди по строкам плана, найди ту, что упоминает orders,
    # и посмотри, начинается ли её описание со SCAN или SEARCH
    for row in cur.fetchall():
        detail = str(row[-1])
        if "orders" not in detail.lower():
            continue
        if detail.startswith("SCAN"):
            return "SCAN"
        if detail.startswith("SEARCH"):
            return "SEARCH"
    return "UNKNOWN"


def main():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    # создай таблицу orders, налей 1000 строк, сними план до и после индекса
    orders_table = """
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total INTEGER
    )
    """
    cur.execute(orders_table)
    for i in range(1000):
        cur.execute("INSERT INTO orders (user_id, product_id, quantity, total) VALUES (?, ?, ?, ?)", (i, i, i, i))
    conn.commit()
    print(plan_operation(cur, "SELECT * FROM orders WHERE user_id = ?", (999,)))
    cur.execute("CREATE INDEX idx_orders_user_id ON orders (user_id)")
    conn.commit()
    print(plan_operation(cur, "SELECT * FROM orders WHERE user_id = ?", (999,)))


if __name__ == "__main__":
    main()