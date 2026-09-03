
STAGE_NAMES = {
    "dns": "DNS-запрос",
    "tcp": "TCP-подключение",
    "server": "Обработка на сервере",
    "transfer": "Передача данных",
    "render": "Рендеринг на клиенте",
}

measurements = {
    "dns": 0.05,
    "tcp": 0.20,
    "server": 2.50,
    "transfer": 0.80,
    "render": 0.45,
}

def report(stages):
    total_time = sum(measurements[stage] for stage in stages)
    slowest_stage = max(stages, key=lambda stage: measurements[stage])
    print(f"Время загрузки: {total_time:.2f} секунд")
    print(f"Узкое место: {STAGE_NAMES[slowest_stage]}")

report(["dns", "tcp", "server", "transfer", "render"])