# Развёртывание SFMShop

Как выложить магазин: локально, в Docker и в облако. Выбор площадки по нагрузке — [hosting_comparison.md](hosting_comparison.md) и [hosting_strategy.md](hosting_strategy.md). Kubernetes — [k8s_deployment.md](k8s_deployment.md).

## Что выкладываем

FastAPI (`uvicorn src.api.main:app`, порт **8000**), PostgreSQL, Redis. Пароли и хосты — из окружения (`Settings` в `src/core/config.py`), не из кода. Образ: `docker/Dockerfile` (multi-stage).

## Локально

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
uvicorn src.api.main:app --reload --port 8000
```

Нужны живые Postgres и Redis на `localhost`, если не используете Docker. Проверка: `curl http://localhost:8000/products`.

## Docker Compose

Из корня репозитория:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Сервисы `app`, `db` (PostgreSQL), `redis` в сети `sfmshop`. Данные БД и Redis — тома `postgres_data` и `redis_data`. В контейнере `DB_HOST=db`, `REDIS_HOST=redis`.

Остановка: `docker compose -f docker/docker-compose.yml down`. Тома сохраняются, пока не сделать `down -v`.

## Облако и PaaS

Учебный и демо-контур: **Render / Railway / Fly.io** — Dockerfile, порт 8000, те же `DB_*` и `REDIS_HOST`.

Ожидаемые **128 RPS** и пик **~190**: **AWS** (ALB + ECS или EKS, RDS, ElastiCache), см. [hosting_strategy.md](hosting_strategy.md).

Секреты (`DB_PASSWORD`, `SECRET_KEY`) задают в панели хостинга или в Kubernetes Secret, не коммитят. `.env` в git не попадает.

## CI перед выкладкой

Push в `main` / `develop` и PR в `main` запускают `.github/workflows/ci.yml`: PostgreSQL, ruff, mypy, `pytest --cov=src` с порогом **80%**. Job `deploy` — только после зелёного `test` и только на **push в main**.
