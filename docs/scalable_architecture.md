# Масштабируемая архитектура для SFMShop

Целевой контур: **5000+ RPS** на витрине, пики распродаж (кратный рост GET) и **отказоустойчивость** без потери заказов. Учебный код уже разделяет чтение и запись (`get_session(read_only=True)`), кэш Redis (`CacheService`) и сессии вне процесса API — это база для горизонтали. `BackgroundTasks` в процессе uvicorn для 5000 RPS **недостаточно**: пик и рестарт требуют очереди вне API.

Смежные документы: [system_design.md](system_design.md), [db_scaling_strategy.md](db_scaling_strategy.md), [db_architecture.md](db_architecture.md). Учебный балансировщик Least Connections — `src/scripts/load_balancer_demo.py`.

Предположение о смеси трафика (типичный магазин): **~90% GET витрины**, остальное — логин, карточки с промахом кэша, `POST /orders`. 5000 RPS почти целиком закрывают CDN + Redis; primary PostgreSQL держит узкий поток checkout.

```text
Клиент
  │
  ▼
CDN (статика, Cache-Control витрины)
  │  miss / POST / авторизованные
  ▼
Балансировщик (Least Connections, health check)
  ├── api-1  ─┐
  ├── api-2  ─┼─ FastAPI (stateless)
  └── api-N  ─┘
        │
        ├─► Redis Cluster     кэш каталога, сессии
        ├─► PG primary        POST /orders, stock
        ├─► PG replicas       GET при промахе кэша, история
        ├─► очередь Redis     письма, оплата, process-orders
        │         └─► workers (N реплик)
        └─► MongoDB           логи (best-effort)
```

---

## Компоненты:

Каждый компонент закрывает одну роль. Смешивать их (кэш заказов в Redis, логи в PostgreSQL) ломает и нагрузку, и отказоустойчивость.

| Компонент | Роль в SFMShop | Что уже есть в коде / что добавить |
|-----------|----------------|-----------------------------------|
| **CDN** | Отдаёт повторные `GET /products` и статику с края сети по `Cache-Control: public, max-age=3600`. Снимает RPS с API на пике витрины. | Заголовки в API уже заданы; origin — балансировщик. `POST /orders` и сессии на CDN не кэшируются (`no-store`). |
| **Балансировщик** | Распределяет живые соединения по API. Алгоритм — **Least Connections** (как в `LoadBalancer`): пиковый долгий `POST /orders` не забивает один узел, пока соседи свободны. | Учебная модель — `load_balancer_demo.py`. В проде — Nginx/HAProxy/ALB + health check `/health`. |
| **API-серверы** | FastAPI/uvicorn: валидация, Bearer→Redis, оркестрация кэша и БД. **Stateless**: сессия не в памяти процесса, инстансы можно добавлять и убивать. | `src/api/main.py`. Несколько реплик за LB. Rate limit (slowapi) — защита origin, не замена CDN. |
| **Кэш (Redis)** | Cache-aside каталога (`products:all`, `product:{id}`, TTL 1 ч) и сессии (`session:*`, 24 ч). Hit на витрине не ходит в PostgreSQL. | `CacheService`. На 5000 RPS — отдельный Redis (cluster/sentinel), не сопроцесс API. |
| **БД (PostgreSQL)** | Источник истины: `users`, `products`, `orders`, `order_items`. Primary — запись и списание `stock`. Replica — промах кэша и история. | `get_session(read_only=...)`. Шарды по `user_id` — только когда primary не держит запись. |
| **Очередь** | Пик и фон: уведомления, оплата, `POST /orders/process-background`. API отвечает сразу, воркеры читают очередь. Переживает рестарт API. | Сейчас `BackgroundTasks` в процессе. Цель — Redis Streams / очередь + workers (как слой Redis в [database_architecture.md](database_architecture.md)). |
| **Логи (MongoDB)** | Append access/error, не на пути checkout. | `LogService`. Сбой MongoDB не останавливает заказ. |

Поток пикового GET: CDN (hit) → клиент; miss → LB → API → Redis (hit) → JSON; miss Redis → replica PostgreSQL → `SETEX`. Поток заказа: LB → API → Redis-сессия → **только primary** (транзакция) → инвалидация кэша → опционально enqueue воркеру.

---

## Масштабирование:

Правило: **сначала вертикаль узкого места, потом горизонталь того слоя, который насытился.** CDN и кэш масштабируют чтение; primary масштабирует запись иначе, чем API.

### Вертикальное (больше CPU/RAM/диска на узел)

| Слой | Что увеличивать | Когда |
|------|-----------------|--------|
| API | CPU и RAM uvicorn-воркера | p99 растёт, а RPS на инстанс ещё низкий; мало соединений, высокий CPU на JSON/Pydantic |
| Redis | RAM (рабочий набор ключей каталога + сессии) | eviction горячих `products:*`, падение hit ratio |
| PostgreSQL primary | CPU, RAM (shared_buffers), диск IOPS | `POST /orders` упирается в locks/`VACUUM`/диск, реплики уже сняли SELECT |
| Replica | RAM под кэш ОС и индексы каталога | промахи Redis бьют в медленный SELECT |
| Воркер | CPU под пакетную обработку | очередь растёт, API при этом здоров |

Вертикаль primary имеет потолок. Её не заменяют «ещё одним API»: лишние инстансы только усиливают lock contention на `stock`.

### Горизонтальное (больше узлов)

| Слой | Как | Условие добавить ресурс |
|------|-----|-------------------------|
| **CDN** | Шире PoP, выше hit | Пик GET, origin RPS ползёт вверх при стабильном hit Redis |
| **Балансировщик** | Active-passive пара (или anycast) | Один LB — SPOF; failover при падении health check |
| **API** | +N реплик FastAPI за LB | CPU инстанса > ~70% **или** p99 витрины > цели **или** очередь соединений на LB; сессии в Redis — можно scale-out без sticky sessions |
| **Redis** | Реплика / cluster по слотам | RAM одного узла не держит ключи **или** нужен failover кэша |
| **PostgreSQL replica** | +read replica за пулом чтений | Hit Redis < ~85% на пике **или** lag/CPU существующих replica |
| **PostgreSQL запись** | Вертикаль → затем шарды по `user_id` | Реплики есть, а primary всё ещё saturates на `create_order` |
| **Воркеры** | +N consumers очереди | Глубина очереди растёт > порога дольше окна пика |
| **MongoDB** | Ротация, отдельный узел | Поток логов конкурирует за диск с полезной нагрузкой (лучше не доводить до одной машины с PG) |

### Пиковая нагрузка (распродажа)

1. CDN и `max-age` держат повторяющиеся GET — основной объём 5000+ RPS.
2. Автомасштабирование API по CPU / p99 / глубине очереди LB (добавить реплики за минуты).
3. Rate limit на origin (`slowapi`) режет ботов; честные клиенты идут в CDN.
4. Checkout не масштабировать «как витрину»: очередь сглаживает фон (письма, process-orders), **списание остатка остаётся синхронным на primary**, иначе оверселл.
5. После пика — scale-in API и воркеров; primary не уменьшают импульсивно.

Оценка: при hit CDN+Redis ≥ 90% на 5000 RPS origin видит сотни RPS. Несколько API-реплик и одна primary с репликами чтения этого достаточно, пока доля `POST /orders` мала. Рост доли checkout — сигнал вертикали/шардов БД, не десятков API.

---

## Отказоустойчивость:

Цель: падение **одного** API, реплики или Redis не теряет оформленные заказы. Падение primary останавливает checkout — это ожидаемо (источник истины); витрина может жить на CDN/кэше короткое время.

### Health checks

| Проверка | Кто опрашивает | Поведение |
|----------|----------------|-----------|
| `GET /health` (процесс жив) | Балансировщик, 2–5 с | 5xx/timeout → инстанс **out of pool** (как `release` слота в демо LB) |
| `GET /health/ready` (Redis ping + пул PG) | Оркестратор / LB | Не ready — не слать трафик; иначе каскад 500 |
| Реплика PostgreSQL: lag < порога | Пул чтений | Отстающую replica исключить из витрины |
| Воркер: heartbeat очереди | Мониторинг | Нет heartbeat → рестарт / не ack сообщений |

Least Connections работает только по **живым** бэкендам: мёртвый узел с «нулем соединений» иначе заберёт весь трафик.

### Резервное копирование

| Данные | Как | RPO / зачем |
|--------|-----|-------------|
| PostgreSQL (заказы, остатки) | Непрерывный WAL + ночной `pg_basebackup`/`pg_dump`; replica как кандидат failover (Patroni и аналоги) | RPO минуты или меньше: деньги нельзя потерять |
| Redis | AOF/RDB **опционально** | Кэш восстанавливается из PG; сессия — повторный логин. Бэкап Redis не заменяет PG |
| MongoDB логи | Периодический dump / TTL-индекс | Допустима потеря хвоста; не блокирует магазин |
| Очередь | Персистентность брокера (Redis Streams / диск) | Задача не теряется при рестарте API, в отличие от `BackgroundTasks` |

Failover primary → replica только с fencing (один писатель). Split-brain опаснее простоя витрины.

### Мониторинг и деградация

- **Алерты:** error rate 5xx, p99, RPS origin vs CDN, cache hit, replication lag, глубина очереди, disk primary, saturation CPU API.
- **Трассировка:** `request_id` в логах MongoDB и в middleware API — связать медленный `POST /orders` с SQL.
- **Деградация:** нет Redis → витрина с replica (выше latency, магазин жив); нет MongoDB → checkout жив; нет очереди → синхронно только критичный путь, фон отложен; нет primary → витрина read-only, заказ 503.
- **Лимиты:** 429 на origin при шторме; идемпотентность воркеров (повтор сообщения после рестарта).

---

## Метрики:

Цели для контура **5000+ RPS** (витрина + фон). Checkout сознательно строже по ошибкам и слабее по RPS.

| Метрика | Цель | Где мерить |
|---------|------|------------|
| **RPS витрины** (`GET /products`, карточка) | **≥ 5000** устойчиво; пик ×2–3 без ошибки origin | CDN + origin; не путать с RPS primary |
| **RPS origin API** | Сотни–низкие тысячи при высоком hit CDN/Redis | Балансировщик |
| **RPS `POST /orders`** | Десятки–сотни; не цель 5000 | Primary; рост — емкость БД, не API |
| **Latency витрина p50** | **< 50 мс** при cache hit (CDN или Redis) | CDN / API middleware (`log_requests`) |
| **Latency витрина p99** | **< 200 мс** | Хвост = miss + replica; если выше — hit ratio или lag |
| **Latency checkout p99** | **< 500 мс** при здоровом primary | Транзакция + lock `stock` |
| **Availability** | **99.9%** успешных запросов витрины за месяц (≈ 43 мин простоя); checkout — тот же SLO **пока жив primary**, иначе честный 503 | Синтетика `/health` + реальные 5xx |
| **Error rate** | 5xx < **0.1%** витрины; 429 отдельно (не как простой) | LB, API |
| **Cache hit ratio** | **≥ 90%** `products:*` на пике | Redis `INFO` / метки в API |
| **Replication lag** | Ниже порога, с которого replica исключают | `pg_stat_replication` |
| **Глубина очереди** | Разгребается в окне пика; рост > N минут — +воркеры | Брокер |

Дополнительно: saturation CPU API (~scale-out при > 70%), eviction Redis, диск WAL primary. Скрипт `measure_api_performance` в `src/api/main.py` — точечный замер; для 5000 RPS нужны агрегаты p50/p99 и RPS с балансировщика, не один `curl`.

**Итог:** 5000+ RPS на SFMShop достигаются **CDN + Redis + несколько stateless API за Least Connections**, а не одним uvicorn. Отказоустойчивость — health check и выведение больных узлов, WAL-бэкапы заказов, мониторинг hit/lag/очереди. Узкое место пика оформления — PostgreSQL primary; его не подменяют кэшем.
