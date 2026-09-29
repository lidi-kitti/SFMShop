# Развёртывание SFMShop в Kubernetes

Манифесты в `k8s/` поднимают **три реплики** FastAPI за Service типа LoadBalancer. Поды stateless: сессии в Redis (`REDIS_HOST`), заказы в PostgreSQL. Имена переменных совпадают с кодом: `src/database/connection.py` читает `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`; `src/services/cache_service.py` — `REDIS_HOST`.

Смежные документы: [scalable_architecture.md](scalable_architecture.md) (зачем несколько API за балансировщиком), [system_design.md](system_design.md).

```text
Клиент
  │
  ▼
Service LoadBalancer  :80  →  targetPort 8000
  ├── pod sfmshop × 3  (Deployment replicas)
  │         ├─► PostgreSQL  DB_HOST=db
  │         └─► Redis       REDIS_HOST=redis
```

---

## Манифесты

| Файл | Зачем |
|------|--------|
| `k8s/deployment.yaml` | Deployment `sfmshop-deployment`: **replicas: 3**, labels `app: sfmshop`, контейнер на порту **8000**, env как в коде, `DB_PASSWORD` из Secret |
| `k8s/service.yaml` | Service `sfmshop-service` типа **LoadBalancer**, selector `app: sfmshop`, порт **80** → **8000** |
| `k8s/hpa.yaml` | HorizontalPodAutoscaler: 2–8 реплик по CPU 60% (нужны `resources.requests.cpu` у контейнера — они заданы в Deployment) |

Selector Deployment и Service должны совпадать (`app: sfmshop`), иначе трафик на поды не попадёт.

---

## Secret с паролем БД

Пароль **не** кладём в `deployment.yaml`. Его читает `os.getenv("DB_PASSWORD")`, в под он попадает через `secretKeyRef`.

Создать Secret до применения Deployment:

```bash
kubectl create secret generic sfmshop-secret \
  --from-literal=DB_PASSWORD='user'
```

Ключ в Secret должен называться `DB_PASSWORD` — так же, как `secretKeyRef.key` в манифесте.

Проверка (значение не печатается целиком в `get secret`):

```bash
kubectl get secret sfmshop-secret
```

Если Secret нет, поды зависают в `CreateContainerConfigError`: контейнер не может подставить `DB_PASSWORD`.

Смена пароля: обновить Secret и перезапустить поды (`kubectl rollout restart deployment/sfmshop-deployment`), иначе старые процессы держат прежний env.

---

## Деплой

Образ тот же, что в Docker: `uvicorn src.api.main:app` на **8000**. Собрать и отдать кластеру (Docker Desktop / minikube):

```bash
docker build -t sfmshop:latest -f docker/Dockerfile .
```

Для minikube: `eval $(minikube docker-env)` до `docker build`, либо `minikube image load sfmshop:latest`. В манифесте `imagePullPolicy: IfNotPresent` — локальный тег подхватывается без registry.

Порядок apply:

```bash
kubectl create secret generic sfmshop-secret --from-literal=DB_PASSWORD='user'
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

PostgreSQL и Redis в этом контуре — отдельные сервисы с DNS-именами `db` и `redis` (как `DB_HOST` / `REDIS_HOST`). Их поднимают своим манифестом или Helm; без них API стартует, а витрина и checkout получат ошибки соединения.

Проверка:

```bash
kubectl get pods -l app=sfmshop
kubectl get svc sfmshop-service
kubectl logs -l app=sfmshop --tail=50
```

Три пода в `Running`. `EXTERNAL-IP` у LoadBalancer на облаке появляется через минуты; локально часто `localhost` или `minikube service sfmshop-service`.

Запрос: `GET http://<EXTERNAL-IP>/products` (с хоста Service это порт **80**, внутри пода — **8000**).

---

## Масштабирование

Поды API не хранят сессию в памяти — можно менять число реплик без sticky sessions.

Вручную (фиксированное число, HPA не спорит, пока его нет):

```bash
kubectl scale deployment sfmshop-deployment --replicas=5
kubectl get pods -l app=sfmshop
```

Вернуть к учебным трём:

```bash
kubectl scale deployment sfmshop-deployment --replicas=3
```

По CPU (урок HPA, файл `k8s/hpa.yaml`):

```bash
kubectl apply -f k8s/hpa.yaml
kubectl get hpa sfmshop-hpa
```

HPA держит от **2** до **8** реплик при средней загрузке CPU **60%**. Это горизонталь слоя API из [scalable_architecture.md](scalable_architecture.md); запись заказов по-прежнему упирается в primary PostgreSQL, а не в число подов.

Откат манифестов:

```bash
kubectl delete -f k8s/hpa.yaml -f k8s/service.yaml -f k8s/deployment.yaml
kubectl delete secret sfmshop-secret
```
