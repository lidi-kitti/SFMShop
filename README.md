  # SFMShop

Учебный интернет-магазин на Python: модели предметной области, PostgreSQL и REST API на FastAPI.

## Стек

- Python 3.12+
- FastAPI + httpx
- PostgreSQL (`psycopg2-binary`)

## Структура

```
SFMShop/
├── docs/                  # спецификация API и учебные заметки
├── src/
│   ├── api/               # FastAPI-приложение
│   ├── database/          # подключение к БД, SQL, запросы
│   ├── models/            # Product, Order, User, Payment и др.
│   ├── utils/             # валидация, расчёты, обработка заказов
│   ├── data/              # тестовые текстовые данные
│   └── main.py            # учебные примеры и демо
├── requirements.txt
└── README.md
```

## Быстрый старт

### 1. Виртуальное окружение

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
source .venv/Scripts/activate
```

### 2. Зависимости

```bash
pip install -r requirements.txt
```

### 3. База данных

1. Создайте БД `sfmshop` в PostgreSQL.
2. Выполните схему и тестовые данные:

```bash
psql -U postgres -d sfmshop -f src/database/create_sfmshop_db.sql
```

Пароль берётся из переменной окружения `DB_PASSWORD` (по умолчанию `user`):

```powershell
$env:DB_PASSWORD = "your_password"
```

```bash
export DB_PASSWORD=your_password
```

### 4. Запуск API

Из корня проекта:

```bash
uvicorn src.api.main:app --reload --port 8000
```

Базовый URL по спецификации: `http://localhost:8000/api/v1`  
(текущее приложение пока монтирует маршруты без префикса `/api/v1` — см. `src/api/main.py`).

Проверка:

```bash
curl http://localhost:8000/products
```

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
| [docs/api_specification.txt](docs/api_specification.txt) | REST API |
| [docs/http_methods_guide.txt](docs/http_methods_guide.txt) | HTTP-методы |
| [docs/postgresql_vs_mongodb_sfmshop_analysis.md](docs/postgresql_vs_mongodb_sfmshop_analysis.md) | PostgreSQL vs MongoDB |
| [docs/git_workflow_summary.md](docs/git_workflow_summary.md) | Git-воркфлоу |
| [docs/web_process_description.txt](docs/web_process_description.txt) | Как работает веб-запрос |

## .gitignore

Игнорируются `.venv/`, `__pycache__/`, `.env`, логи, кэши тестов и IDE.  
Если `__pycache__` уже попал в индекс:

```bash
git rm -r --cached src/__pycache__ src/models/__pycache__ src/utils/__pycache__
```
