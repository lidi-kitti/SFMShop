# Файл src/database/models.py
from sqlalchemy import Integer, String, Numeric, ForeignKey, DateTime, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, joinedload
from datetime import datetime, timezone
from decimal import Decimal

class Base(DeclarativeBase):
    pass

class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    # Связь с заказами
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Product(Base):
    """Модель товара"""
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0)


class Order(Base):
    """Модель заказа"""
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default='pending')
    order_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    """Позиция заказа"""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column()
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()

# Настройка подключения: запись — primary, чтение — replica
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

from src.core.config import settings


def _database_url(host, port):
    user = quote_plus(settings.db_user)
    password = quote_plus(settings.db_password or "")
    return f"postgresql://{user}:{password}@{host}:{port}/{settings.db_name}"


primary_engine = create_engine(
    _database_url(
        settings.db_host or settings.db_primary_host,
        settings.db_port,
    )
)
replica_engine = create_engine(
    _database_url(
        settings.db_replica_host or settings.db_host or settings.db_primary_host,
        settings.db_replica_port or settings.db_port,
    )
)

engine = primary_engine
PrimarySession = sessionmaker(bind=primary_engine)
ReplicaSession = sessionmaker(bind=replica_engine)


def get_session(read_only=False):
    """Сессия к основной БД или к реплике для чтения."""
    if read_only:
        return ReplicaSession()
    return PrimarySession()

def get_user_orders_orm(session, user_id):
    """Получить заказы пользователя через ORM с оптимизацией N+1"""
    orders = session.execute(
        select(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .where(Order.user_id == user_id)
    ).unique().scalars().all()
    return orders