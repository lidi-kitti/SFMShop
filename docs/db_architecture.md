# Архитектура БД SFMShop

SFMShop — интернет-магазин: каталог, пользователи, заказы, сессии витрины и служебные события (логи API, ошибки). Эти нагрузки **различаются по структуре, согласованности и доступу**. Одна СУБД на все роли либо усложняет модель, либо проигрывает по задержке и объёму.

Поэтому проект использует **polyglot persistence**:

| Роль | СУБД | Задача |
|------|------|--------|
| Источник истины | **PostgreSQL** | Пользователи, товары, заказы, позиции заказов |
| Горячий слой | **Redis** | Кэш витрины и пользователей, сессии |
| События | **MongoDB** | Access/error логи API |

Правило границ: **PostgreSQL отвечает на «что правда»; Redis — на «что быстро отдать сейчас»; MongoDB — на «что произошло».** Сбой Redis не уничтожает заказ. Сбой MongoDB не останавливает checkout. Сбой PostgreSQL останавливает магазин.

Смежные документы: критерии выбора — [database_selection.md](database_selection.md); сравнение PostgreSQL и MongoDB как ядра — [postgresql_vs_mongodb_sfmshop_analysis.md](postgresql_vs_mongodb_sfmshop_analysis.md); реплики и шарды — [db_scaling_strategy.md](db_scaling_strategy.md).

---

## 1. Схема архитектуры

```text
                         ┌─────────────────────┐
                         │   Клиент            │
                         │   FastAPI           │
                         │   src/api/main.py   │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │   Приложение        │
                         │   models / queries  │
                         │   CacheService      │
                         │   LogService        │
                         └──┬────────┬──────┬──┘
              ACID, JOIN    │        │      │  append
              primary/replica        │      │
                            │        │      │
         ┌──────────────────▼─┐  ┌───▼────┐ │  ┌──────────────────┐
         │   PostgreSQL       │  │ Redis  │ │  │   MongoDB        │
         │   source of truth  │  │        │ │  │   sfmshop_logs   │
         │                    │  │ кэш    │ │  │                  │
         │  users             │  │ сессии │ │  │  logs            │
         │  products          │  │        │ │  │    type=access   │
         │  orders            │  └────────┘ │  │    type=error    │
         │  order_items       │             │  └──────────────────┘
         │                    │             │
         │  primary ──WAL──►  │             │
         │  replica (чтение)  │             │
         └────────────────────┘             │
```

В коде это три клиента: SQLAlchemy (`src/database/models.py`), `CacheService` (`src/services/cache_service.py`), `LogService` (`src/services/log_service.py`).

---

## 2. Карта данных: что где лежит

### 2.1. PostgreSQL — пользователи, товары, заказы

Источник истины. Схема — `src/database/models.py`.

| Сущность | Таблица | Почему здесь |
|----------|---------|--------------|
| Пользователь | `users` | Уникальный `email`, FK от заказов, `Numeric` баланс, долгоживущая запись |
| Товар | `products` | Цена `Numeric(10, 2)`, остаток `stock`, каталог общий для всех |
| Заказ | `orders` | FK на `users.id`, сумма `total`, статус; транзакция вместе с позициями и остатком |
| Позиция заказа | `order_items` | FK на `orders.id` и `products.id`; цена на момент покупки |

Запись — на primary (`DB_PRIMARY_HOST`, `get_session()`). Чтение витрины и списков — с replica (`get_session(read_only=True)`, в API — `get_read_db`).

**Не кладём сюда:** сессии (TTL, высокая частота записи), сырые логи API. Они раздувают бэкапы ядра и конкурируют с `POST /orders` за I/O.

### 2.2. Redis — кэш и сессии

Не источник истины. Данные восстанавливаются из PostgreSQL или истекают по TTL.

| Назначение | Ключ | TTL | Почему здесь |
|------------|------|-----|--------------|
| Кэш каталога | `products:all` | 1 час | Список витрины читают чаще, чем меняют |
| Кэш карточки | `product:{id}` | 1 час | Точечный GET без SQL |
| Кэш пользователей | `users:all`, `user:{id}` | 1 час | Те же чтения списка и карточки |
| Сессия | `session:{uuid}` | 24 часа | Кто залогинен, без строки в `users` на каждый запрос |

Реализация — `CacheService`: `GET`/`SETEX`/`DEL`. Cache-aside в API: сначала Redis, при промахе — replica PostgreSQL, затем запись в Redis. После `COMMIT` на primary кэш сбрасывается (`invalidate_products`, `invalidate_product`, `invalidate_users`).

**Не кладём сюда:** заказы и остатки. Persistence Redis слабее WAL PostgreSQL; eviction и TTL противоречат «заказ живёт годы».

Очереди (`queue:email`, `queue:payment`) — слой расширения: HTTP checkout не должен ждать SMTP. В текущем коде очередей нет.

### 2.3. MongoDB — логи

Документное хранилище без FK на заказы. База `sfmshop_logs`, коллекция `logs`. Запись — `insert_one`, **не** в одной транзакции с PostgreSQL.

| Тип документа | Поля | Почему здесь |
|---------------|------|--------------|
| `access` | `ip`, `endpoint`, `method`, `status_code`, `timestamp` | `LogService.log_access` |
| `error` | `message`, `stack_trace`, `timestamp` | `LogService.log_error` |
| произвольный | любой набор полей | `LogService.save_log` |

Выборки — фильтры по `type`, `status_code`, `ip`, диапазону `timestamp`, агрегация `$group`. JOIN с заказами не нужен. Потеря одной записи лога не ломает оформление.

**Не кладём сюда:** пользователей, каталог и заказы. Нет классических FK; целостность «заказ + позиции + пользователь» уезжает в приложение.

Коллекции `events` / `analytics` — расширение (доменные события и воронка кликов). Сейчас в коде есть только `logs`.

---

## 3. Обоснование выбора СУБД по задачам

Выбор — соответствие модели данных и гарантий нагрузке, а не универсальность одного движка.

### 3.1. PostgreSQL: ядро магазина

**Задачи:** регистрация пользователя, каталог как источник истины, оформление заказа, история и отчёты.

| Критерий | Как проявляется в SFMShop |
|----------|---------------------------|
| Связи | Один пользователь — много заказов; заказ — много позиций; позиция ссылается на товар. `ForeignKey` на `users.id`, `orders.id`, `products.id`. JOIN собирает «заказ + товары + пользователь» (`get_user_orders_orm`, `get_user_order_history`) |
| ACID | Один `COMMIT`: `orders` + `order_items` + `products.stock -= n`. `SELECT … FOR UPDATE` на товар. Уникальный `email`, `Numeric(10, 2)` |
| Стабильная схема | Поля заказа и товара меняются редко; контракт версионируется DDL |
| Долговечность | Заказ и оплата переживают рестарт приложения, `FLUSHALL` в Redis и сбой MongoDB |

Почему не MongoDB: нет классических FK; «заказ без пользователя» и отчёты уезжают в приложение или в `$lookup`. Почему не Redis: RAM, нет JOIN и денежных ограничений, TTL противоречит сроку жизни заказа.

### 3.2. Redis: витрина и сессии

**Задачи:** быстрый `GET /products` и `GET /users`, карточки, короткоживущая сессия.

| Критерий | Как проявляется в SFMShop |
|----------|---------------------------|
| Ключ–значение, O(1) | `GET products:all`, `GET product:{id}`, `GET session:{uuid}` — без JOIN |
| TTL | Кэш — 3600 с, сессия — 86400 с. Истечение ключа — штатный способ забыть данные |
| Ослабленная согласованность | Витрина может отставать до TTL или до `invalidate_*`. Для карточки это приемлемо; для списания остатка — нет (остаток только в PostgreSQL) |
| Нагрузка | Каталог читают чаще, чем меняют. Cache-aside разгружает replica |

Почему не PostgreSQL: кэш в той же БД, что заказы, не разгружает primary и не даёт естественного TTL. Почему не MongoDB: выше латентность, чем у in-memory KV; нет `SETEX` как основного API.

После потери Redis каталог восстанавливается из PostgreSQL. Сессию пользователь создаёт заново — заказ от этого не исчезает.

### 3.3. MongoDB: логи API

**Задачи:** access-лог запроса, error-лог исключения, статистика по типам и статус-кодам.

| Критерий | Как проявляется в SFMShop |
|----------|---------------------------|
| Гибкая схема | У access есть `endpoint` и `status_code`, у error — `message` и `stack_trace`. `save_log` принимает словарь |
| Append-only | Поток `insert_one` велик относительно изменения схемы. TTL-индекс по `timestamp` естественнее бесконечной таблицы рядом с `orders` |
| Запросы без JOIN | `get_logs_by_type`, `get_logs_by_status_code`, `get_logs_by_ip`, `get_logs_statistics` (`$group`) |
| Слабая связь с деньгами | Падение `insert_one` не откатывает заказ |

Почему не PostgreSQL: жёсткая схема или JSONB-«простыня»; рост таблицы конкурирует с `VACUUM` и бэкапами заказов. Почему не Redis: RAM и eviction конфликтуют с «найти ошибки за неделю».

---

## 4. Потоки данных

### 4.1. Создание заказа — `POST /orders`

Три хранилища участвуют в одном запросе, не подменяя друг друга.

```text
Клиент
  │  POST /orders  {user_id, items: [{product_id, quantity}]}
  ▼
API (src/api/main.py)
  │
  │  1. (расширение) Redis GET session:{id}  →  user_id
  │
  │  2. PostgreSQL primary — одна транзакция
  │     BEGIN
  │       проверка User
  │       SELECT Product … FOR UPDATE
  │       INSERT orders, order_items
  │       UPDATE products.stock
  │     COMMIT
  │
  │  3. Redis после COMMIT
  │     DEL products:all
  │     DEL product:{id}   для каждого купленного товара
  │
  │  4. (расширение) MongoDB log_access / событие order_created
  ▼
Ответ: {id, user_id, total, status, items}
```

| Шаг | Сейчас в коде | Расширение |
|-----|----------------|------------|
| Сессия | `CacheService.get_user_session` | Проверка в `POST /orders` |
| Запись | `create_order` в `src/api/main.py`: заказ + позиции + `stock` | — |
| Инвалидация | `invalidate_products` / `invalidate_product` сразу после `COMMIT` | — |
| Лог | `LogService.log_access` / `log_error` | Вызов из API; коллекция `events` |

**Порядок гарантий**

1. Сначала PostgreSQL. Если `COMMIT` не прошёл (нет товара, FK, мало `stock`) — Redis и MongoDB не трогаем.
2. Инвалидация Redis только после `COMMIT`. Удалить ключ до записи опасно: параллельный `GET /products` успеет положить в Redis старый остаток.
3. MongoDB — best effort: заказ уже существует, лог можно потерять или дописать позже.

Следующий `GET` только что созданного заказа — на **primary** (read-your-writes). Реплика может отстать. Кэша заказа нет и не должно быть как источника истины.

### 4.2. Просмотр витрины — `GET /products`

```text
GET /products
  → Redis GET products:all
       попадание → JSON
       промах    → PostgreSQL replica
                 → Redis SETEX products:all 3600
                 → JSON
```

То же для `GET /products/{id}`, `GET /users`, `GET /users/{id}`. Запись в PostgreSQL нет. Лог access в MongoDB — опционально и не в критическом пути витрины.

### 4.3. Регистрация — `POST /users`

```text
POST /users {name, email, balance}
  → PostgreSQL primary INSERT users
  → при уникальном email: COMMIT, затем Redis DEL users:all
  → при дубликате: IntegrityError → 409, Redis не трогаем
```

---

## 5. Что будет, если перепутать роли

| Если сделать так | Следствие |
|------------------|-----------|
| Заказы в MongoDB | Риск заказа без пользователя, дубли цен, сложные отчёты |
| Каталог и остатки только в Redis | После рестарта пустая витрина; оверселл; нет истории |
| Логи в той же БД, что заказы | Раздувание бэкапов ядра, конкуренция I/O с `create_order` |
| Сессии в PostgreSQL на каждый клик | Лишняя запись на primary ради данных с TTL 24 часа |

Сбой Redis — просела витрина и слетели сессии, заказы целы. Сбой MongoDB — нет логов, магазин жив. Сбой PostgreSQL — магазин стоит.

---

## 6. Минусы гибридной схемы

Между БД **нет общей транзакции**.

| Ситуация | Что происходит |
|----------|----------------|
| `COMMIT` прошёл, `DEL products:all` нет | Витрина показывает старый `stock` до TTL (до часа) |
| `COMMIT` прошёл, лог в MongoDB нет | Заказ есть, в аналитике его нет |
| Реплика отстаёт, кэш уже сброшен | `GET /products` читает replica и кладёт в Redis ещё не обновлённый каталог |

Цена гибрида: три клиента, три DSN, три контура бэкапа и мониторинга. Это плата за то, что ни одна СУБД не выполняет чужую роль.

---

## 7. Сводка

```text
                    SFMShop
                       │
     ┌─────────────────┼─────────────────┐
     ▼                 ▼                 ▼
PostgreSQL           Redis            MongoDB
users                products:all     logs (access, error)
products             product:{id}
orders               users:all
order_items          user:{id}
                     session:{uuid}
     │                 │                 │
  ACID, FK, JOIN    TTL, O(1)           документ, append
  деньги и связи    скорость            «что произошло»
```

| Вопрос | Ответ |
|--------|--------|
| Где правда о заказе и остатке? | PostgreSQL, и только там |
| Откуда витрина берёт список товаров? | Redis; при промахе — replica PostgreSQL |
| Кто пользователь в этом запросе? | Redis `session:*` |
| Где логи API? | MongoDB `sfmshop_logs.logs` |
| Когда сбрасывать кэш? | Сразу после успешного `COMMIT` на primary |
