import requests
import time
from requests.exceptions import RequestException, Timeout, ConnectionError
from typing import Optional

class ExchangeRateClient:
    """Клиент для работы с API курсов валют"""

    def __init__(self, base_url: str = "https://api.exchangerate-api.com/v4/latest"):
        self.base_url = base_url
        self.timeout = 5
        self.max_retries = 3

    def get_exchange_rate(
        self,
        base_currency: str,
        target_currency: str
        ) -> Optional[float]:
        """Получить курс валют с обработкой ошибок и retry"""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    f"{self.base_url}/{base_currency}",
                    timeout=self.timeout
                    )
                response.raise_for_status()
                data = response.json()

                if target_currency in data.get("rates", {}):
                    return data["rates"][target_currency]
                else:
                    print(f"Валюта {target_currency} не найдена")
                    return None

            except Timeout:
                if attempt < self.max_retries - 1:
                    delay = 2 ** attempt # Экспоненциальная задержка
                    print(f"Таймаут, повтор через {delay} сек...")
                    time.sleep(delay)
                else:
                    print("Превышено время ожидания после всех попыток")
                    return None

            except ConnectionError:
                if attempt < self.max_retries - 1:
                    delay = 2 ** attempt
                    print(f"Ошибка подключения, повтор через {delay} сек...")
                    time.sleep(delay)
                else:
                    print("Ошибка подключения после всех попыток")
                    return None

            except RequestException as e:
                print(f"Ошибка запроса: {e}")
                return None

    def convert_price(
        self,
        price: float,
        from_currency: str,
        to_currency: str
        ) -> Optional[float]:
        """Конвертировать цену из одной валюты в другую"""
        if from_currency == to_currency:
            return price

        rate = self.get_exchange_rate(from_currency, to_currency)
        if rate is None:
            return None

        return price * rate

ExchangeClient = ExchangeRateClient

if __name__ == "__main__":
    client = ExchangeRateClient()
    converted_price = client.convert_price(1000, "USD", "RUB")
    if converted_price is not None:
        print(f"1000 USD = {converted_price} RUB")
    else:
        print("Не удалось получить курс валют")