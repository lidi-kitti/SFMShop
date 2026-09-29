# Сравнение хостингов для проекта SFMShop

SFMShop — FastAPI на порту **8000**, источник заказов — PostgreSQL (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`), кэш и сессии — Redis (`REDIS_HOST`), логи — MongoDB. Образ уже собирается из `docker/Dockerfile`, три реплики API описаны в [k8s_deployment.md](k8s_deployment.md). Ниже — куда это класть: свой сервер, облако гиперскейлера или PaaS.

Смежные документы: [system_design.md](system_design.md), [scalable_architecture.md](scalable_architecture.md), [k8s_deployment.md](k8s_deployment.md).

Критерии сравнения для магазина: скорость выкладки демо, цена на малых RPS, кто чинит диск и бэкапы, как рядом живут Postgres + Redis, готовность к пику витрины (CDN + горизонталь API) без оверселла на `POST /orders`.

---

## VPS

Один (или несколько) виртуальных серверов: Timeweb, Selectel, Hetzner, DigitalOcean Droplet. Вы ставите Docker Compose / nginx сами, как в `docker/docker-compose.yml`.

**Преимущества:**

- Предсказуемая цена: фиксированный тариф, нет сюрприза за egress, как у AWS.
- Полный контроль: свои версии Postgres/Redis, свои `DB_*` в `.env`, те же тома, что в учебном compose.
- Понятный путь «с ноутбука на сервер»: `docker compose up`, systemd, nginx → `:8000`.
- Хороший тренажёр админки: SSL, файрвол, бэкап `pg_dump` — то, чего PaaS прячет.

**Недостатки:**

- Один VPS = одна точка отказа: рестарт, диск, DDoS — падают и витрина, и checkout.
- Масштаб из [scalable_architecture.md](scalable_architecture.md) (несколько API, replica Postgres, Redis отдельно) — это уже несколько машин и ручной LB, не «кнопка».
- Бэкапы, обновления ОС, мониторинг диска — ваша смена. Для заказов это риск, не экономия.
- Нет managed Postgres «из коробки»: реплика и PITR надо собирать самим.

**Когда уместно:** учебный контур, один продавец, трафик вроде домашнего стенда. Не как единственный прод на распродажу.

---

## Cloud (AWS, Google Cloud)

IaaS + managed-сервисы: EC2/GCE или сразу ECS/GKE/EKS; RDS / Cloud SQL; ElastiCache / Memorystore; ALB / Cloud Load Balancing; S3/Cloud Storage под статику и бэкапы.

**Преимущества:**

- Слои SFMShop ложатся на готовые продукты: API — автоскейл за LB, заказы — RDS primary, витрина — read replica, кэш — managed Redis, логи — отдельный диск или Cloud Logging вместо Mongo на той же ВМ, что Postgres.
- Регионы и AZ: падение одной зоны не обязано убить checkout, если primary с Multi-AZ.
- Совпадает с манифестами `k8s/`: GKE/EKS, Secret для `DB_PASSWORD`, HPA как в `hpa.yaml`.
- Пик GET: Cloud CDN + `Cache-Control` витрины; запись по-прежнему на один primary — это ограничение домена, не хостинга.

**Недостатки:**

- Счёт за сеть, NAT, простой RDS «на всякий случай». Учебный магазин легко переплатить.
- Крутая кривая: IAM, VPC, security groups. Ошибка в SG важнее, чем `uvicorn` на VPS.
- Vendor lock по обвязке (RDS endpoint, IAM-роли), не по FastAPI-коду.

**Когда уместно:** боевой магазин, цель **5000+ RPS** витрины, нужна replica и отдельный Redis, команда готова платить за managed и разбирать биллинг.

---

## PaaS (Railway, Render, Fly.io)

Платформа забирает сборку из Dockerfile / GitHub, даёт HTTPS и обычно managed Postgres (иногда Redis) по кнопке. Деплой близок к job `deploy` в `.github/workflows/ci-cd.yml`: зелёные тесты → выкладка.

**Преимущества:**

- Самый короткий путь «репозиторий → URL»: Dockerfile SFMShop, порт 8000, env как в `.env.example` (`DB_HOST` = внутренний hostname сервиса БД).
- Postgres и часто Redis — отдельные сервисы, не «всё на одном VPS». Пароль не в git, как Secret в k8s.
- Автодеплой с `main` после CI, preview-приложения на PR.
- Fly.io удобен, если нужны машины ближе к пользователю; Render/Railway — проще UI для учебного дедлайна.

**Недостатки:**

- Потолок и цена растут ступеньками: сон бесплатного инстанса, лимиты CPU, дорогой исходящий трафик на витрине.
- Не все три хранилища (Postgres + Redis + Mongo + RabbitMQ) одинаково «родные»: Mongo/очередь часто внешние (Atlas, CloudAMQP) или их режут.
- Меньше контроля над сетью и диском, чем у VPS; меньше рычагов HA, чем у AWS/GCP Multi-AZ.
- Смена платформы — перенос томов и DNS, не только смена `DB_HOST`.

**Когда уместно:** демо для ментора, MVP, пока RPS низкий и команда не хочет админить Linux. Не замена Cloud на пике распродажи.

---

## Сводка

| | **VPS** | **Cloud (AWS, GCP)** | **PaaS (Railway, Render, Fly.io)** |
|--|---------|----------------------|-------------------------------------|
| Выкладка демо | Средне (SSH, compose, nginx) | Долго (VPC, IAM) | Быстро (Git + Dockerfile) |
| Postgres + Redis рядом | Сами | RDS + ElastiCache / Cloud SQL + Memorystore | Обычно кнопкой, Mongo/очередь — отдельно |
| Горизонталь API | Ручной LB | ALB/GCLB, K8s HPA | Ограниченный scale сервиса |
| Цена на стенде | Низкая и плоская | Легко завысить | Низкий старт, ступени при росте |
| Отказоустойчивость checkout | Слабая (один узел) | Сильная (AZ, managed primary) | Средняя (платформа, не Multi-AZ из коробки) |
| Совпадение с учебным k8s | Compose на машине | EKS/GKE как в `k8s/` | Свой оркестратор, манифесты не обязательны |

---

## Выбор для SFMShop

**Оптимально сейчас (учёба, демо, CI → URL): PaaS**, предпочтительно **Render** или **Railway**: есть Dockerfile, те же `DB_*` / `REDIS_HOST`, деплой с `main` после `.github/workflows/ci-cd.yml`, без админки Linux. **Fly.io** — если важны регионы ближе к клиенту.

**Следующий шаг, когда витрина и заказы — уже продукт:** **Cloud (AWS или GCP)** — managed Postgres + Redis, LB, CDN, при необходимости тот же Kubernetes, что в репозитории. Так закрывается цель из [scalable_architecture.md](scalable_architecture.md), а не тариф Droplet.

**VPS** оставляем для лабораторной работы «поднять прод руками» и дешёвого личного стенда, не как единственную площадку для денег и остатков на складе.

Итого: **PaaS для текущего контура SFMShop, Cloud — когда появятся SLA и пик RPS, VPS — только как учебный или временный хост.**
