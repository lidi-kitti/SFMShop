# Файл src/api/schemas.py
import html
import re

from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(gt=0, le=10_000_000)
    quantity: int = Field(ge=0, le=100_000)
    category: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        sanitized = html.escape(v.strip())
        if not sanitized:
            raise ValueError("Имя товара не может быть пустым")
        return sanitized

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        pattern = r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-]+$"
        if not re.match(pattern, v):
            raise ValueError("Категория содержит недопустимые символы")
        return v.strip()