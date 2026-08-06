# Git Workflow для проекта SFMShop

## Использованные команды Git

По истории и веткам в репозитории использовались (или подразумеваются) типичные операции:

- `git init` — инициализация репозитория (коммит «Инициализация проекта SFMShop»)
- `git add`, `git commit` — фиксация изменений по файлам (`product.py`, `user.py`, `main.py`, `.gitignore` и др.)
- `git branch`, `git switch` / `git checkout` — работа на отдельных ветках; текущая ветка: `feature/add-shipping`
- `git merge` — слияния веток (в т.ч. merge commit «Объединены изменения из main», слияние с `origin/main`, merge PR #1)
- `git push`, `git pull` — синхронизация с удалённым `origin` (есть `remotes/origin/*`)
- экспериментальные сценарии: ветки `feature/test-rebase`, `feature/test-stash`, `feature/test-conflict` (rebase / stash / конфликтное слияние)

## Созданные ветки

**Локальные**

| Ветка | Назначение (по коммитам и имени) |
|--------|----------------------------------|
| `main` | основная линия разработки; коммиты про `get_total_price`, слияния с конфликтами и с remote |
| `master` | ранняя точка («Add .gitignore»), параллельно с историей до `feature/test` |
| `feature/add-email-validation` | валидация email в `User` (`src/models/user.py`) |
| `feature/add-inventory-management` | методы управления складом в `Product` |
| `feature/add-shipping` | метод `calculate_shipping` в `Product`, merge из `main` с `get_category` |
| `feature/test-conflict` | отдельные правки `get_total_price` (участвовали в конфликтном merge) |
| `feature/test-rebase` | ветка с коммитом «Добавлен другой комментарий» в `product.py` |
| `feature/test-stash` | коммит «Добавлены уроки блока 2: ООП» (`src/main.py`) |
| `feature/test` | изменение `.gitignore` |

**Удалённые (`origin`)**

- `origin/main`
- `origin/feature/add-email-validation`
- `origin/feature/add-inventory-management`
- `origin/feature/add-shipping`

## Разрешённые конфликты

- **Коммит `41dc851` («Разрешен конфликт в get_total_price и добавлен комменатарий в user»)** — конфликтное слияние линий `main` (коммит `1ccd589`, изменён `get_total_price` в `src/models/product.py`) и ветки `feature/test-conflict` (коммит `05c2a50`, тоже `get_total_price` в том же файле); в итоге учтены обе правки и добавлен комментарий в `user`.

## Статистика по ключевым коммитам (`git log --stat`)

- **Merge в `feature/add-shipping`** (`b97b8e6`): объединение `6656368` (расчёт доставки в `product.py`) и `main`/`fdcfaab` (`get_category` в `product.py`, +2 строки).
- **Скидки** (`299c4d8`): `src/models/product.py` (+4 −1 строка).
- **Склад** (`c7d3e61`): `src/models/product.py` (+6 строк).
- **Email** (`a51cc8f`): `src/models/user.py` (+1 строка); на GitHub — **Merge pull request #1** (`9924929`).
- **Инициализация** (`cd1680d`): первый массовый импорт проекта (38 файлов, +1071 строка).

## Стратегия работы с ветками

- **`main`** — центральная ветка для интеграции; есть расхождение с локальным состоянием до синхронизации с `origin/main` (видно по графу: `origin/main`, merge remote-tracking branch).
- **Feature-ветки** — отдельные задачи (валидация email, склад, доставка, учебные ветки test/test-conflict/test-rebase/test-stash).
- **Публикация** — часть фич запушена в `origin`; релиз фичи email прошёл через **Pull Request #1**.
- Текущая активная точка истории (**HEAD**): **`feature/add-shipping`**, синхронизирована с **`origin/feature/add-shipping`** после merge из `main`.
