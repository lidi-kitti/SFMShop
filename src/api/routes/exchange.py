from fastapi import APIRouter, Depends, HTTPException, Query, Request

from src.services.external_api_service import (
    CurrencyNotFoundError,
    ExchangeClient,
    ExchangeRateError,
)

router = APIRouter(prefix="/exchange", tags=["exchange"])


def get_exchange_client(request: Request) -> ExchangeClient:
    return request.app.state.exchange_client


@router.get("/rate")
async def get_exchange_rate(
    base: str = Query("USD", min_length=3, max_length=3),
    target: str = Query("RUB", min_length=3, max_length=3),
    client: ExchangeClient = Depends(get_exchange_client),
):
    """Курс валют с внешнего API (retry внутри клиента)."""
    try:
        rate = await client.get_exchange_rate(base, target)
    except CurrencyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ExchangeRateError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "base": base.upper(),
        "target": target.upper(),
        "rate": rate,
    }


@router.get("/convert")
async def convert_amount(
    amount: float = Query(..., gt=0),
    base: str = Query("USD", min_length=3, max_length=3),
    target: str = Query("RUB", min_length=3, max_length=3),
    client: ExchangeClient = Depends(get_exchange_client),
):
    """Конвертация суммы (например, цены товара) по текущему курсу."""
    try:
        rate = await client.get_exchange_rate(base, target)
    except CurrencyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ExchangeRateError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "amount": amount,
        "base": base.upper(),
        "target": target.upper(),
        "rate": rate,
        "converted": round(amount * rate, 2),
    }
