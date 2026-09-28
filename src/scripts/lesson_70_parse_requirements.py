# Создай файл scripts/lesson_70_parse_requirements.py
import re

# Учебный фрагмент requirements.txt для разбора (не файл проекта)
REQUIREMENTS = """\
fastapi==0.104.1
uvicorn==0.24.0
# веб-сервер и фреймворк выше

pytest==7.4.3
psycopg2-binary==2.9.9
redis==5.0.1
sqlalchemy>=2.0.0
pika
"""

_REQ_LINE = re.compile(
    r"^([A-Za-z0-9][A-Za-z0-9_.-]*)\s*(===|==|!=|~=|>=|<=|>|<)?\s*([^#\s]+)?"
)


def parse_requirements(text):
    # Разбери строки на (имя, оператор, версия), пропусти пустые и комментарии
    parsed = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = _REQ_LINE.match(line)
        if not match:
            continue
        name, operator, version = match.groups()
        parsed.append((name, operator or "", version or ""))
    return parsed


def main():
    # Посчитай зафиксированные (==) и незафиксированные, выведи отчёт
    deps = parse_requirements(REQUIREMENTS)
    pinned = [name for name, operator, _ in deps if operator == "=="]
    unpinned = sorted(name for name, operator, _ in deps if operator != "==")

    print(f"Всего зависимостей: {len(deps)}")
    print(f"Зафиксировано (==): {len(pinned)}")
    print(f"Не зафиксировано: {len(unpinned)}")
    print("Незафиксированные пакеты:")
    for name in unpinned:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
