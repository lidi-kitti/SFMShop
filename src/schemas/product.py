from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):
    """Схема ответа API для товара."""

    id: int
    name: str
    price: float
    quantity: int = Field(validation_alias="stock")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
