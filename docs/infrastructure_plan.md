# План инфраструктуры SFMShop

Как связаны Docker, Kubernetes и CI/CD. Нагрузка и выбор облака — [hosting_strategy.md](hosting_strategy.md). Сравнение хостингов — [hosting_comparison.md](hosting_comparison.md).

```text
Разработчик  ──push──►  GitHub Actions (ci.yml)
                              │ test: Postgres + pytest --cov
                              │ deploy: только main
                              ▼
                         образ / PaaS / AWS
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
           FastAPI         PostgreSQL       Redis
          (8000)           DB_HOST           REDIS_HOST
```

## Docker

| Файл | Роль |
|------|------|
| `docker/Dockerfile` | Два этапа: зависимости, затем `uvicorn src.api.main:app --host 0.0.0.0 --port 8000` |
| `docker/docker-compose.yml` | Сервисы **app**, **db**, **redis**, сеть **sfmshop**, тома данных Postgres и Redis |

Compose поднимает магазин одной командой. Приложение не ходит на `localhost` внутри сети: хост БД — имя сервиса `db`.

## Kubernetes

| Файл | Роль |
|------|------|
| `k8s/deployment.yaml` | Три реплики API, `DB_*` и `REDIS_HOST`, пароль из Secret |
| `k8s/service.yaml` | LoadBalancer, порт 80 → 8000 |
| `k8s/hpa.yaml` | Автомасштаб 2–8 подов по CPU |

Подробности: [k8s_deployment.md](k8s_deployment.md). Имеет смысл, когда origin стабильно большой (в уроке — выше **1000 RPS**) или нужна та же модель, что в облаке (EKS).

## CI/CD

`.github/workflows/ci.yml` (дублирует полный контур `ci-cd.yml`):

1. **test** — сервис PostgreSQL, переменные `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
2. `ruff check`, `mypy`, `pytest tests --cov=src --cov-fail-under=80`.
3. **deploy** — `needs: test`, только ветка **main**.

Локально то же покрытие: `pytest tests --cov=src`.

## Переменные

Единственный класс настроек — `Settings` в `src/core/config.py`. Шаблон — `.env.example`, локальная копия — `.env` (в `.gitignore`).
