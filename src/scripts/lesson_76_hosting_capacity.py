from dataclasses import dataclass
from math import ceil

HEADROOM = 1.5


@dataclass(frozen=True)
class Endpoint:
    name: str            # имя эндпоинта SFMShop
    expected_rps: float  # ожидаемая нагрузка, запросов/сек
    avg_ms: float        # средняя длительность одного запроса, мс


def worker_capacity(avg_ms: float) -> float:
    """Пропускная способность одного воркера: запросов в секунду."""
    return 1000 / avg_ms


def workers_needed(ep: Endpoint, headroom: float) -> int:
    """Сколько воркеров нужно эндпоинту с учётом запаса headroom."""
    return ceil(ep.expected_rps * headroom / worker_capacity(ep.avg_ms))


def tier(total_rps: float) -> str:
    """Выбор тарифа по суммарному RPS (пороги из урока)."""
    if total_rps < 100:
        return "VPS/PaaS"
    if total_rps <= 1000:
        return "Cloud"
    return "Cloud + K8s"


def main():
    endpoints = [
        Endpoint("catalog", 60.0, 40.0),
        Endpoint("cart", 25.0, 80.0),
        Endpoint("checkout", 8.0, 250.0),
        Endpoint("search", 35.0, 120.0),
    ]
    rows = sorted(endpoints, key=lambda ep: ep.name)
    worker_counts = [workers_needed(ep, HEADROOM) for ep in rows]
    total_rps = sum(ep.expected_rps for ep in rows)
    total_workers = sum(worker_counts)

    print(f"{'endpoint':<12} {'rps':>8} {'avg_ms':>8} {'workers':>8}")
    print("-" * 40)
    for ep, n in zip(rows, worker_counts):
        print(f"{ep.name:<12} {ep.expected_rps:>8.1f} {ep.avg_ms:>8.1f} {n:>8}")
    print("-" * 40)
    print(f"Суммарный RPS: {total_rps:.1f}")
    print(f"Воркеров: {total_workers}")
    print(f"Тариф: {tier(total_rps)}")


if __name__ == "__main__":
    main()
