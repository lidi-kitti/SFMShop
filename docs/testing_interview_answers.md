# Ответы на вопросы о тестировании

Примеры ниже — из учебного магазина **SFMShop** (`tests/`, `src/scripts/lesson_66_*` … `lesson_68_*`).

## Вопрос 1: Какой у тебя подход к тестированию?

Ответ: сначала фиксирую контракт самой дешёвой проверки, потом поднимаюсь к границам системы.

В SFMShop домен (`Product`, `User`, `Order`) и формулы (`src/utils/calculations.py`) покрываю юнит-тестами: фикстуры, `assert`, без сети. Новую формулу веду через TDD: сначала красный тест, потом код. Внешние стороны — Redis, HTTP курсов, PostgreSQL — в тестах не поднимаю: мокаю точку вызова. HTTP-слой проверяю `TestClient` по `src/api/main.py`, патча имена там, где их ищет код (`get_cached_products` в `cache_service`, `create_order` в `queries`).

Пирамида: много юнитов → меньше API с моками → живой брокер/БД только руками, не в CI-уроке. Тест должен ломаться вместе с регрессией, а не из‑за «Mongo не слушает 27017».

## Вопрос 2: Какие типы тестов ты пишешь?

Ответ: в проекте три слоя.

1. **Юнит-тесты домена и утилит** — `tests/test_models.py`, `tests/test_utils.py`. Pytest, `@pytest.fixture` (`sample_order`), `@pytest.mark.parametrize` для `calculate_discount`, `calculate_total`, `calculate_delivery_discount` (4999 → платная доставка, от 5000 → 0).
2. **Юнит-тесты сервисов с моками** — `tests/test_services.py`: `ExchangeClient.get_exchange_rate` через `patch('src.services.exchange_client.requests.get')`; курс есть / валюты нет. Учебный `OrderService` в `lesson_68_order_service_mocks.py`: успех, пустой заказ, падение БД.
3. **API-тесты** — `tests/test_api.py`: `GET /products` (200, три товара из кэша) и `POST /orders` с телом `{user_id, product_id, quantity}` (200, `id` и `message`) без живых Postgres и Redis.

Отдельно `unittest.TestCase` в скриптах уроков 66–67, когда нужно программно напечатать «запущено / провалено / ошибок».

## Вопрос 3: Как мокаешь зависимости и зачем?

Ответ: мок — замена соседа, не самой логики. Патчу **там, где имя резолвится при вызове**, не «файл, где функция написана», если её уже импортировали в другой модуль.

В SFMShop:

- HTTP курса: `@patch('src.services.exchange_client.requests.get')` + `MagicMock.json.return_value = {"rates": {"RUB": 92.5}}`. Без `api.exchangerate-api.com`.
- Оформление заказа: `db.create_order.return_value = 42`; при `side_effect = RuntimeError` проверяю `notifier.send.assert_not_called()`.
- API: `@patch('src.services.cache_service.get_cached_products')` и `@patch('src.database.queries.create_order')`, потому что `main.py` ходит в модуль-источник, а не делает `from ... import create_order`.

Мок не подменяет бизнес-правило: скидку за количество и порог доставки 5000 проверяю на реальной функции.

## Вопрос 4: Что такое TDD и как ты его применял?

Ответ: сначала тест, который падает, потом минимум кода, затем рефакторинг при зелёных тестах.

`calculate_delivery` уже была в уроке — красного этапа на ней нет. Рядом добавили `calculate_delivery_discount`. Красный этап: тест в `test_utils.py` импортирует имя, которого нет → `ImportError: cannot import name 'calculate_delivery_discount'`. Зелёный: в `calculations.py` «от 5000 — 0, иначе вся `delivery_cost`». Рефакторинг: константа `FREE_DELIVERY_FROM = 5000`, тесты остались зелёными вместе с `calculate_discount` / `calculate_total` / `calculate_delivery`.

Тот же цикл в `lesson_67_apply_discount_tdd.py`: до 3 шт без скидки, 3–5 → 5%, от 6 → 10%; `apply_discount(100, 2/4/10) = 200 / 380 / 900`.

## Вопрос 5: Как понимаешь, что тестов достаточно? Нужно ли 100% coverage?

Ответ: достаточно, когда покрыты правила денег и границы сбоя, а не каждая строка `print`.

В SFMShop гоняю `pytest tests --cov=src`. Порог урока — **выше 80%**, не 100%: `__main__` демо, скрипты, живой Rabbit/Mongo в coverage не гоняю. Смотрю ветки: пустой заказ, отрицательная цена, нет валюты в JSON, Redis/БД недоступны, порог доставки 4999 vs 5000.

Coverage без осмысленного assert бесполезен: зелёный процент при одном `assert True` ничего не ловит. Фикстура + параметризация дешевле, чем копипаста трёх почти одинаковых тестов. Если тест требует поднятый RabbitMQ — это не юнит, его не смешиваю с `test_models.py`.
