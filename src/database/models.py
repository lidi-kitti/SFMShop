# Файл src/database/models.py
from sqlalchemy import Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Связь с заказами
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Product(Base):
    """Модель товара"""
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantity: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Order(Base):
    """Модель заказа"""
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Связь с пользователем
    user: Mapped["User"] = relationship(back_populates="orders")

# Настройка подключения
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Получить сессию БД"""
    return SessionLocal()