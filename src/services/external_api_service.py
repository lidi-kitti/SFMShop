import asyncio
import logging

import httpx
from httpx import HTTPStatusError, RequestError, TimeoutException

logger = logging.getLogger(__name__)


class ExchangeRateError(Exception):
    """Не удалось получить курс после всех попыток."""


class CurrencyNotFoundError(ExchangeRateError):
    """В ответе API нет запрошенной валюты."""


class ExchangeClient:
    """Асинхронный клиент курсов валют с retry и экспоненциальной паузой."""

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        base_url: str = "https://api.exchangerate-api.com/v4/latest",
        timeout: float = 5.0,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = client
        self._owns_client = client is None

    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get_exchange_rate(self, base: str, target: str) -> float:
        """Асинхронное получение курса валют с retry."""
        base = base.upper()
        target = target.upper()
        if base == target:
            return 1.0

        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = await self._http().get(
                    f"{self.base_url}/{base}",
                    timeout=self.timeout,
                )
                response.raise_for_status()
                rates = response.json().get("rates") or {}
                if target not in rates:
                    raise CurrencyNotFoundError(
                        f"Валюта {target} не найдена для базы {base}"
                    )
                return float(rates[target])
            except CurrencyNotFoundError:
                raise
            except TimeoutException as exc:
                last_error = exc
                logger.warning(
                    "Таймаут курса %s→%s, попытка %s/%s",
                    base,
                    target,
                    attempt + 1,
                    self.max_retries,
                )
            except HTTPStatusError as exc:
                last_error = exc
                if exc.response.status_code < 500:
                    raise ExchangeRateError(
                        f"Внешний API вернул {exc.response.status_code}"
                    ) from exc
                logger.warning(
                    "HTTP %s для курса %s→%s, попытка %s/%s",
                    exc.response.status_code,
                    base,
                    target,
                    attempt + 1,
                    self.max_retries,
                )
            except RequestError as exc:
                last_error = exc
                logger.warning(
                    "Ошибка запроса курса %s→%s: %s, попытка %s/%s",
                    base,
                    target,
                    exc,
                    attempt + 1,
                    self.max_retries,
                )

            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)

        raise ExchangeRateError(
            f"Не удалось получить курс {base}→{target} после {self.max_retries} попыток"
        ) from last_error

    async def convert_price(self, price: float, base: str, target: str) -> float:
        """Перевести цену товара SFMShop в другую валюту."""
        rate = await self.get_exchange_rate(base, target)
        return round(price * rate, 2)
