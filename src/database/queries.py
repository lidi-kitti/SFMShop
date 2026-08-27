import sys
from pathlib import Path
from contextlib import contextmanager
from time import perf_counter

from sqlalchemy import Index, func, select
from sqlalchemy.orm import joinedload


def _setup_import_paths():
    """Добавляет src, src/models и src/database в sys.path для запуска файла из любой оболочки."""
    src_root = Path(__file__).resolve().parent.parent
    db_dir = Path(__file__).resolve().parent
    for path in (src_root / "models", src_root, db_dir):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


_setup_import_paths()
from models import Order, OrderItem, Product, User, engine, get_session


@contextmanager
def _session_scope(commit=False):
    session = get_session()
    try:
        yield session
        if commit:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_order_statistics():
    with _session_scope() as session:
        stmt = (
            select(
                Order.user_id,
                func.count(Order.id).label("order_count"),
                func.sum(Order.total).label("total_sum"),
            )
            .group_by(Order.user_id)
            .order_by(func.sum(Order.total).desc())
        )
        return session.execute(stmt).all()


def get_user_order_history(user_id):
    with _session_scope() as session:
        stmt = (
            select(
                Order.id.label("order_id"),
                Order.created_at,
                Product.name.label("product_name"),
                OrderItem.quantity,
                Product.price,
            )
            .join(OrderItem, OrderItem.order_id == Order.id)
            .join(Product, Product.id == OrderItem.product_id)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return session.execute(stmt).all()


def get_user_orders(user_id):
    """Заказы пользователя через relationship User.orders."""
    with _session_scope() as session:
        user = session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        if user is None:
            return []
        return list(user.orders)


def get_all_orders_with_users():
    """Все заказы с пользователями одним запросом (без N+1)."""
    with _session_scope() as session:
        stmt = select(Order).options(joinedload(Order.user))
        return session.execute(stmt).unique().scalars().all()


def get_top_products(limit=5):
    """Топ товаров по количеству продаж."""
    with _session_scope() as session:
        try:
            stmt = (
                select(
                    Product.id,
                    Product.name,
                    func.sum(OrderItem.quantity).label("total_sold"),
                )
                .join(OrderItem, OrderItem.product_id == Product.id)
                .group_by(Product.id, Product.name)
                .order_by(func.sum(OrderItem.quantity).desc())
                .limit(limit)
            )
            return session.execute(stmt).all()
        except Exception as e:
            print(f"Ошибка при получении топ товаров: {e}")
            return []


def get_orders_with_products(user_id):
    """Заказы пользователя с товарами."""
    with _session_scope() as session:
        try:
            stmt = (
                select(Order.id, Product.name, OrderItem.quantity, Product.price)
                .join(OrderItem, OrderItem.order_id == Order.id)
                .join(Product, Product.id == OrderItem.product_id)
                .where(Order.user_id == user_id)
            )
            return session.execute(stmt).all()
        except Exception as e:
            print(f"Ошибка при получении заказов с товарами: {e}")
            return []


def create_order(user_id, total):
    """Создать заказ через ORM и вернуть id."""
    session = get_session()
    try:
        order = Order(user_id=user_id, total=total)
        session.add(order)
        session.commit()
        return order.id
    except Exception as e:
        session.rollback()
        print(f"Ошибка при создании заказа: {e}")
        raise
    finally:
        session.close()


def generate_sales_report(start_date):
    with _session_scope() as session:
        try:
            stmt = select(
                func.coalesce(func.sum(Order.total), 0),
                func.count(Order.id),
            ).where(Order.created_at >= start_date)
            total, count = session.execute(stmt).one()
            return {
                "total": float(total),
                "count": count,
                "average": float(total) / count if count > 0 else 0,
            }
        except Exception as e:
            print(f"Ошибка при генерации отчета о продажах: {e}")
            raise


def calculate_total_revenue(start_date, end_date):
    with _session_scope() as session:
        stmt = select(
            func.coalesce(func.sum(Order.total), 0),
            func.count(Order.id),
        ).where(Order.created_at.between(start_date, end_date))
        total, count = session.execute(stmt).one()
        return {
            "total": float(total),
            "count": count,
            "average": float(total) / count if count > 0 else 0,
        }


def measure_index_performance():
    """Измерение производительности запросов с индексами."""
    with _session_scope(commit=True) as session:
        print("Тест 1: Поиск товара по названию")

        start_time = perf_counter()
        session.execute(select(Product).where(Product.name == "Ноутбук")).scalar_one_or_none()
        time_without_index = perf_counter() - start_time

        Index("idx_products_name", Product.name).create(bind=engine, checkfirst=True)

        start_time = perf_counter()
        session.execute(select(Product).where(Product.name == "Ноутбук")).scalar_one_or_none()
        time_with_index = perf_counter() - start_time

        print(f"  Без индекса: {time_without_index:.6f} сек")
        print(f"  С индексом: {time_with_index:.6f} сек")
        if time_with_index > 0:
            print(f"  Ускорение: {time_without_index / time_with_index:.2f}x")

        print("\nТест 2: Поиск заказов по пользователю")

        start_time = perf_counter()
        session.execute(select(Order).where(Order.user_id == 1)).scalars().all()
        time_without_index = perf_counter() - start_time

        Index("idx_orders_user_id", Order.user_id).create(bind=engine, checkfirst=True)

        start_time = perf_counter()
        session.execute(select(Order).where(Order.user_id == 1)).scalars().all()
        time_with_index = perf_counter() - start_time

        print(f"  Без индекса: {time_without_index:.6f} сек")
        print(f"  С индексом: {time_with_index:.6f} сек")
        if time_with_index > 0:
            print(f"  Ускорение: {time_without_index / time_with_index:.2f}x")

def get_all_products():
    with _session_scope() as session:
        stmt = select(Product.id, Product.name, Product.price, Product.quantity)
        rows = session.execute(stmt).mappings().all()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "price": float(row["price"]),
                "quantity": row["quantity"],
            }
            for row in rows
        ]