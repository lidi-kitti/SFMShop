from fastapi import APIRouter, Depends, HTTPException

from src.dependencies import get_product_service
from src.schemas.product import ProductResponse
from src.services.product_service import ProductService


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    """Получение товара по ID."""
    try:
        return await service.get_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
