# Архитектура асинхронной обработки заказов для проекта SFMShop

После `POST /orders` источник истины уже в PostgreSQL: заказ, позиции и списание `stock` в одном `COMMIT` (`create_order` в `src/api/main.py`). HTTP-ответ должен уйти сразу (**201**). Письмо, отчёт и прочий фон в том же запросе увеличивают p99 checkout и теряются при рестарте uvicorn (`BackgroundTasks` в `POST /orders/process-background`).

Поэтому побочные эффекты уходят в **брокер** (Redis Stream / List; учебная модель — `MessageBroker` в `src/scripts/lesson_64_message_broker.py`). Producer — API. Consumer — воркеры (`queue_consumer.py`, прототип — `producer_consumer.py`). Очередь **не** заменяет транзакцию: остаток по-прежнему только на primary.

```text
Клиент ──POST /orders──► FastAPI (Producer)
                              │
                    COMMIT PostgreSQL (заказ + stock)
                              │
                              ▼
                    Redis-очередь  email | warehouse | report | …
                              │
                    ack после успеха
                              ▼
                    N × Consumer     retry → dead-letter
```

Смежные документы: [scalable_architecture.md](scalable_architecture.md), [database_architecture.md](database_architecture.md), комментарии в `src/services/order_service.py`.

## Задачи для очереди

В очередь — работа, которая **не обязана завершиться до ответа клиенту**: внешний I/O, пакеты, повтор без повторного `POST`. В запросе остаются валидация, сессия, транзакция заказа.

| Задача | Триггер | Данные в сообщении | Приоритет | Почему не в HTTP-запросе |
|--------|---------|-------------------|-----------|--------------------------|
| **Отправка email-уведомлений** | `COMMIT` `create_order`; смена статуса (`paid`, `shipped`) | `task=send_email`, `order_id`, `user_id`, `to` (email), `template` (`order_created` / `shipped`), `attempts` | **высокий** — покупатель ждёт письмо, но не страницу 201 | SMTP секунды и таймауты; рестарт API не должен терять «спасибо за заказ» |
| **Обновление склада** (после факта продажи) | Тот же `COMMIT`; опционально массовый `POST /orders/process` | `task=update_stock`, `order_id`, `items[{product_id, quantity}]`, `attempts` | **высокий** | Само списание `stock` уже в транзакции. В очереди — инвалидация Redis (`invalidate_products`), уведомление WMS/поставщика, пересчёт витрины. Держать SMTP/WMS в `create_order` нельзя; повторный lock primary на каждое письмо — тоже |
| **Генерация отчетов** | Конец дня / кнопка админки / пачка обработанных заказов | `task=generate_report`, `period` или `order_ids[]`, `format` (csv/pdf), `attempts` | **низкий** | JOIN и агрегаты (`get_order_statistics`, `generate_sales_report`) конкурируют с checkout на primary. Отчёт строится с replica в фоне |
| **Другие фоновые задачи** | После заказа или по расписанию | см. ниже | средний / низкий | Тоже I/O или CPU вне критического пути |

**Другие фоновые задачи SFMShop** (тот же брокер, отдельные имена `task`):

- **`process_orders`** — то, что сейчас делает `process_orders_async` / `BackgroundTasks`: смена статуса на `processed` без удержания соединения.
- **Оплата / webhook** — вызов payment-service; ответ API — «заказ принят», статус платежа догоняет consumer.
- **Логи в MongoDB** — access/error append, чтобы `LogService` не удлинял checkout.
- **Пересчёт курса / enrich карточки** — внешний `ExchangeClient` с retry уже в сервисе; пакетные обновления цен лучше через очередь, а не из `GET /products`.

Приоритет в брокере: отдельные очереди/группы (`orders.email`, `orders.stock`, `orders.reports`) или поле `priority`. Consumer email/stock читают чаще, чем report. Учебный `MessageBroker` — одна `Queue`; в проде — Redis Stream с consumer group.

Идемпотентность: ключ `order_id + task` (повтор `send_email` не шлёт второе письмо). Складской lock в очереди **не** дублирует `COMMIT`: повтор `update_stock` только сбрасывает кэш / шлёт WMS, не вычитает `stock` ещё раз.

## Надежность

Цель: оформленный заказ не теряется; письмо и отчёт либо доходят, либо видны в dead-letter, а не «тихо пропадают» вместе с процессом API.

### Гарантии доставки

| Механизм | Как в SFMShop |
|----------|----------------|
| **Persistent messages** | Сообщение пишется в брокер с диском (Redis AOF / Rabbit durable / Stream), **после** `COMMIT` PostgreSQL. Память процесса uvicorn не считается хранилищем. `BackgroundTasks` этой гарантии не даёт. |
| **Acknowledgment** | Consumer читает без удаления (или в pending Stream). `ack` / `task_done` — только после успешного handler. Рестарт воркера до ack → сообщение снова доступно другому consumer (at-least-once). |
| **Порядок publish** | Сначала БД, потом `publish`. Если enqueue не удался — заказ уже есть; API логирует и кладёт в outbox/повтор, а не откатывает покупку. |

Семантика — **at-least-once**: письмо может уйти дважды без идемпотентного handler. Exactly-once на SMTP не обещаем.

Учебный контур (`lesson_64_message_broker.py`): `publish` → `Queue.put`; успех handler → лог OK; иначе счётчик `attempts`.

### Retry-логика при ошибках

- Повторять **временные** сбои: таймаут SMTP, 5xx WMS, сеть (как `TimeoutException` / `RequestError` у `ExchangeClient`).
- **Не** повторять 4xx «пользователь без email» без правки данных — сразу в разбор/DLQ.
- Максимум попыток: **3** (как `MessageBroker(max_retries=3)` и retry курса валют).
- Пауза: экспонента `2 ** attempt` секунд (1, 2, 4), чтобы не молотить упавший SMTP.
- Счётчик `attempts` в теле задачи; при неуспехе сообщение **возвращается в очередь** (или delayed queue), не теряется.

Пример из урока: `update_stock` проходит с 3-й попытки; `generate_report` все три раза падает.

### Обработка ошибок и судьба после исчерпания попыток

1. Handler бросает / возвращает false → `attempts += 1`.
2. `attempts < max_retries` → снова в рабочую очередь (RETRY).
3. **`attempts >= max_retries` → dead-letter** (список/очередь `dead_letter`, как в `MessageBroker.dead_letter`): сообщение **не удаляется молча**.
4. Алерт по длине DLQ; оператор повторяет вручную или чинит шаблон письма.
5. Лог в MongoDB (`type=error`, `order_id`, `task`) — без JOIN с `orders`.
6. Заказ в PostgreSQL **не откатывается**: покупатель уже получил 201. DLQ — про фон, не про деньги.

Итог надёжности: persistent + ack дают «не потерять задачу при рестарте»; retry переживает короткий сбой; DLQ даёт наблюдаемый хвост после трёх неудач.

## Масштабирование

Checkout масштабируется primary PostgreSQL; фон — **числом Consumer**, не числом API. Пик `POST /orders` наполняет очередь; воркеры разгребают после пика, API остаётся быстрым.

### Горизонтальное масштабирование Consumer

- Воркеры stateless: читают брокер, ходят в SMTP / replica / Redis. Добавить процесс = +1 consumer в группе (`order_worker` в `producer_consumer.py`, N реплик в [scalable_architecture.md](scalable_architecture.md)).
- Условие scale-out: глубина очереди растёт дольше окна пика **или** lag (время от publish до ack) выше SLO письма (минуты, не часы).
- Scale-in после распродажи, чтобы не держать простой SMTP.
- Разные пулы: много email-воркеров, мало report-воркеров — тяжёлый отчёт не блокирует письма.
- API при росте очереди **не** масштабируют «ещё одним uvicorn ради писем».

### Балансировка нагрузки между воркерами

- ** Competing consumers**: одна группа на очередь; каждое сообщение достаётся одному воркеру (как Least Connections у API, но естественный round-robin брокера).
- Prefetch/QoS ограничен (1–N сообщений на воркера), чтобы один медленный отчёт не забрал всю пачку.
- Длинные `generate_report` — отдельная очередь, иначе email ждёт PDF.
- Учебный `asyncio.Queue(maxsize=5)` ограничивает backpressure producer; в Redis — длина Stream как сигнал «не публиковать быстрее, чем успевают».

### Мониторинг очередей

| Метрика | Зачем |
|---------|--------|
| **Глубина** (length / `XLEN`) по `email`, `stock`, `report` | Рост → +Consumer или деградация SMTP |
| **Lag** publish→ack, отдельно p99 писем | SLO «письмо после заказа» |
| **Rate** publish vs consume | Пик заказов vs отставание фона |
| **Retry / DLQ count** | Как в уроке: `Dead-letter: N`; рост — баг handler или мёртвый провайдер |
| **Redeliveries** до ack | Воркер падает на задаче |
| **CPU воркеров, ошибки 5xx внешних API** | Отличить «мало воркеров» от «лежит почта» |

Алерты: DLQ > 0 дольше N минут; глубина email выше порога. Дашборд рядом с p99 `POST /orders`: очередь может расти при здоровом checkout — это штатный пик, не 500 API.

**Итог:** в очередь SFMShop выносят email, складской фон (кэш/WMS), отчёты и прочий I/O, чтобы `create_order` оставался коротким и транзакционным. Надёжность — диск брокера, ack, 3 retry, dead-letter. Масштаб — добавить Consumer на горячую очередь, развести потоки по приоритету и смотреть глубину, lag и DLQ.
