# Подход к тестированию в проекте SFMShop

## Обзор

Тесты SFMShop держат контракт витрины и checkout без живых PostgreSQL, Redis, RabbitMQ и внешнего API курсов. Юниты проверяют деньги и валидацию (`Product`, `Order`, `calculate_*`). API и клиент валют изолированы моками на точке вызова.

Инструменты: **pytest**, **pytest-cov**, `unittest.mock`, `fastapi.testclient.TestClient`. Учебные циклы TDD/`unittest` живут в `src/scripts/lesson_66_`* … `lesson_69_*` и не смешиваются с папкой `tests/`. Запуск регрессии:

```bash
pytest tests --cov=src --cov-fail-under=80
```

Пирамида: много быстрых тестов моделей и утилит → сервисы со скидками и валидаторами → узкий слой HTTP с `@patch`.

## Типы тестов



### `tests/test_models.py`

Юниты домена. Фикстуры `sample_product` / `sample_user` / `sample_order` собирают объекты в канонической форме: `User(name, email)`, `Product(name, price, quantity)`, `Order(user, products, order_id=...)`.

Покрывают:

- создание и поля (`order_id`, пользователь, список товаров);
- валидацию (`price < 0`, `quantity < 0`, email без `@` / без `.`);
- методы: `get_total_price`, `calculate_price` со стратегией скидки, `Order.calculate_total()` (1000×2 + 500×1 = **2500**), `OrderValidator`, магические методы заказа.



### `tests/test_utils.py`

Чистые функции `src/utils/calculations.py` и `validators.py`:


| Тест                                        | Что покрывает                                                               |
| ------------------------------------------- | --------------------------------------------------------------------------- |
| `test_calculate_discount`                   | `price * discount_rate` (в т.ч. 1000×0.1 = 100)                             |
| `test_calculate_total`                      | `price * quantity` (1000×2 = 2000)                                          |
| `test_calculate_delivery`                   | `weight * distance * 0.1` → для (5, 50) это **25**                          |
| `test_calculate_delivery_discount`          | бесплатная доставка от 5000: (4999, 400)→400, (5000, 400)→0, (12000, 700)→0 |
| `test_validate_age` / `test_validate_email` | порог 18 лет, `@` и `.` в email                                             |
| бенчмарки сумм и поиска                     | `calculate_total_orders*` и индекс товаров                                  |




### `tests/test_api.py`

HTTP и учебный in-memory роутер:

- `test_product_api_crud` — `ProductAPI.handle` из `src/api/router.py` (201/200/404/405/204).
- `test_get_products` — `GET /products` у `app` из `src/api/main.py`. Мок `src.services.cache_service.get_cached_products` (функция объявлена в этом модуле; `main` берёт её как `cache_service_mod.get_cached_products()`, не `from ... import`). Ожидание: **статус 200**, в JSON **три товара** (список, без обёртки `{"products": ...}`).
- `test_create_order` — `POST /orders` с телом `{"user_id": 1, "product_id": 2, "quantity": 1}`. Мок `src.database.queries.create_order` (сигнатура `user_id, product_id, quantity, total` есть в `queries.py`). Ожидание: **статус 200**, поля `id` и `message`**:** `"Заказ создан"` — так отвечает короткий путь эндпоинта, когда нет `items`.

Живые Postgres и Redis в этих тестах не нужны.

### `tests/test_services.py`

Сервисный слой без I/O:

- скидки и валидаторы (`PercentDiscount`, `ProductValidator`, `OrderCalculator`);
- `test_get_exchange_rate` / `test_get_exchange_rate_currency_missing` — `@patch("src.services.exchange_client.requests.get")`. Цель патча совпадает с `import requests` в `exchange_client.py`. Найденный курс: мок `{"rates": {"RUB": 92.5}}` → **92.5**. Нет RUB в `rates` → `None`. Сети к `api.exchangerate-api.com` нет.



## Покрытие кода

Инструмент: **pytest-cov**, отчёт `pytest tests --cov=src`. Конфиг `.coveragerc`: `source = src`, omit учебные `src/scripts/`*, замороженный `src/main.py`, тяжёлый `src/api/main.py` (его контракт проверяет TestClient, не line-coverage), демо с `asyncio.run` при импорте, AI/Mongo/очередь.

Замеренный прогон: **51 passed**, **TOTAL 95%**. Порог урока и CI — **выше 80%** (`--cov-fail-under=80`). 100% по всему репозиторию не цель: `__main__`-демо и живой брокер в coverage не входят (см. `.coveragerc`).

Выкладка и Docker/K8s/CI: [deployment.md](deployment.md), [infrastructure_plan.md](infrastructure_plan.md).


| Компонент                                 | Cover                     |
| ----------------------------------------- | ------------------------- |
| `src/utils/calculations.py`               | 100%                      |
| `src/utils/validators.py`                 | 100%                      |
| `src/models/order.py`, `user.py`          | 100%                      |
| `src/models/product.py`                   | 82% (хвост `if __name__`) |
| `src/api/router.py`, `src/api/schemas.py` | 100%                      |
| `src/services/product_validator.py`       | 91%                       |
| `src/services/discounts.py`               | 93%                       |
| `src/services/order_calculator.py`        | 86%                       |


Порог урока — **выше 80%**. 100% по всему репозиторию не цель: `__main__`-демо и живой брокер в coverage не входят.

## Организация тестов

```text
tests/
  conftest.py          # sys.path: корень проекта, src, src/models (для metaclasses)
  test_models.py
  test_utils.py
  test_api.py          # TestClient(app) на модуле
  test_services.py
```

- Имена файлов `test_*.py`, функции `test_*` — pytest собирает сам.
- **Фикстуры** в `test_models.py` (`sample_product`) и `test_services.py` (`valid_product`); общие пути — в `conftest.py`.
- **Параметризация** в `test_utils.py`: один тест — несколько входов, без копипасты.
- Моки вешаются декоратором `@patch` на функцию теста; клиент API — один `client = TestClient(app)` на модуль.
- Скрипты `src/scripts/lesson_*.py` — отдельный контур `unittest` + печать сводки, не пакет `tests/`. Пример CI-сводки: `lesson_75_order_total_ci.py`.



## Использованные техники

**TDD.** `calculate_delivery` уже была в уроке — красного этапа на ней нет. Для `calculate_delivery_discount` сначала тест в `test_utils.py`, импорт падал с `ImportError: cannot import name 'calculate_delivery_discount'`. Затем реализация: от 5000 ₽ доставка 0, иначе вся `delivery_cost`; порог вынесен в `FREE_DELIVERY_FROM`. Тот же цикл в `lesson_67_apply_discount_tdd.py` и `lesson_69_calculate_total_tests.py`.

**Моки.** Правило *patch where it is looked up*:

- `GET /products` → `@patch("src.services.cache_service.get_cached_products")` — имя определено в `cache_service.py`, `main.py` не делает `from ... import get_cached_products`.
- `POST /orders` → `@patch("src.database.queries.create_order")` — то же для `queries.create_order`.
- курс валют → `@patch("src.services.exchange_client.requests.get")`.

**Фикстуры.** `sample_order` даёт заказ 101 с ноутбуком 1000×2 и мышью 500×1 — и создание, и `calculate_total() == 2500` без дублирования setup.

**Параметризация.** Три кейса бесплатной доставки в одном `test_calculate_delivery_discount`; четыре пары `(price, quantity, expected)` в `test_calculate_total`.

Смежный собеседовательный конспект: [testing_interview_answers.md](testing_interview_answers.md).