# SFMShop

Учебный интернет-магазин на Python: модели предметной области, PostgreSQL и REST API на FastAPI.

# Настройка окружения

Другой разработчик поднимает то же окружение за три шага: создать `venv`, активировать, поставить пакеты из `requirements.txt`.

## Создание виртуального окружения

```bash
python -m venv venv
```

```bash
source venv/bin/activate # Linux/macOS
```

Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

Git Bash:

```bash
source venv/Scripts/activate
```

## Установка зависимостей

В `requirements.txt` — то, что импортирует проект: fastapi, uvicorn, pydantic, pydantic-settings, psycopg2-binary, sqlalchemy[asyncio], asyncpg, aiohttp, httpx, requests, redis, pymongo, pika, passlib[bcrypt], slowapi, python-dotenv, anthropic, chromadb, pytest, pytest-cov.

```bash
pip install -r requirements.txt
```

Проверка (без ошибок, с конкретными версиями в `pip freeze`):

```bash
pip freeze
python -c "import fastapi, psycopg2, redis, pika, pymongo, sqlalchemy"
```

## Обновление requirements.txt

После установки или добавления пакета зафиксировать версии:

```bash
pip freeze > requirements.txt
```

## Стек

- Python 3.12+
- FastAPI, uvicorn, Pydantic, httpx / requests / aiohttp
- PostgreSQL: psycopg2-binary, SQLAlchemy, asyncpg
- Redis, MongoDB (pymongo), RabbitMQ (pika)

## Структура

```
SFMShop/
├── docs/                  # архитектура, тесты, спецификация API
├── tests/                 # pytest: модели, утилиты, API, сервисы
├── src/
│   ├── api/               # FastAPI-приложение
│   ├── database/          # подключение к БД, SQL, запросы
│   ├── models/            # Product, Order, User, Payment и др.
│   ├── services/          # кэш, очередь, курсы валют
│   ├── utils/             # валидация, расчёты, обработка заказов
│   ├── scripts/           # учебные скрипты уроков
│   ├── data/              # тестовые текстовые данные
│   └── main.py            # учебные примеры и демо
├── requirements.txt
├── venv/                  # локально, в git не коммитится
└── README.md
```

## Быстрый старт

### 1. Окружение

```bash
python -m venv venv
source venv/bin/activate          # Windows Git Bash: source venv/Scripts/activate
pip install -r requirements.txt
```

### 2. База данных

1. Создайте БД `sfmshop` в PostgreSQL.
2. Выполните схему и тестовые данные:

```bash
psql -U postgres -d sfmshop -f src/database/create_sfmshop_db.sql
```

Пароль — переменная `DB_PASSWORD` (по умолчанию `user`).

### 3. Запуск API

Из корня проекта, с активированным `venv`:

```bash
uvicorn src.api.main:app --reload --port 8000
```

Проверка: `curl http://localhost:8000/products`

### 4. Тесты

```bash
pytest tests --cov=src
```

Подход к тестам: [docs/testing_approach.md](docs/testing_approach.md).

### 5. Учебные скрипты

```bash
python src/main.py
python src/models/notifications.py
```

## API (кратко)

| Метод  | Путь                 | Описание             |
|--------|----------------------|----------------------|
| GET    | `/products`          | Список товаров       |
| GET    | `/products/{id}`     | Товар по ID          |
| POST   | `/products`          | Создание товара      |
| PUT    | `/products/{id}`     | Обновление товара    |
| DELETE | `/products/{id}`     | Удаление товара      |
| GET    | `/orders`            | Список заказов       |
| POST   | `/orders`            | Создание заказа      |
| GET    | `/users/{id}/orders` | Заказы пользователя  |

Полная спецификация: [docs/api_specification.txt](docs/api_specification.txt).

## Документация

| Файл | О чём |
|------|--------|
| [docs/testing_approach.md](docs/testing_approach.md) | Подход к тестированию |
| [docs/api_specification.txt](docs/api_specification.txt) | REST API |
| [docs/git_workflow_summary.md](docs/git_workflow_summary.md) | Git-воркфлоу |
| [docs/scalable_architecture.md](docs/scalable_architecture.md) | Масштабирование |
| [docs/web_process_description.txt](docs/web_process_description.txt) | Как работает веб-запрос |

## .gitignore

Игнорируются `venv/`, `.venv/`, `__pycache__/`, `.env`, логи, кэши тестов и IDE. Каталог `venv` на другую машину не копируют — его создают заново по разделу «Настройка окружения».
