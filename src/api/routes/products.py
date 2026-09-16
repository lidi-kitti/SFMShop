from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.auth import TokenUser, get_current_user
from src.dependencies import get_product_service
from src.schemas.product import ProductResponse
from src.services.cache_service import CacheService
from src.services.product_service import ProductService


router = APIRouter(prefix="/products", tags=["products"])
cache_service = CacheService()


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


@router.post("", status_code=201, response_model=ProductResponse)
async def create_product(
    body: ProductCreate,
    service: ProductService = Depends(get_product_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """Создать товар. Нужен Authorization: Bearer <jwt>."""
    product = await service.create_product(body.name, body.price, body.stock)
    cache_service.invalidate_products()
    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
    current_user: TokenUser = Depends(get_current_user),
):
    """Получение товара по ID."""
    try:
        return await service.get_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
