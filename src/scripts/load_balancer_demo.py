# Создай отдельный файл scripts/load_balancer_demo.py
class LoadBalancer:
    """Балансировщик нагрузки по алгоритму Least Connections.

    Распределяет запросы между серверами-бэкендами SFMShop,
    выбирая сервер с наименьшим числом активных соединений.
    """

    def __init__(self, servers):
        # Для каждого сервера храним число активных соединений
        self._connections = {name: 0 for name in servers}
        # Порядок добавления — для детерминированного выбора при равенстве
        self._order = list(servers)

    def route(self) -> str:
        """Выбрать сервер с минимумом активных соединений и занять слот.

        При равенстве выбирается первый по порядку добавления.
        """
        best = min(self._order, key=lambda name: self._connections[name])
        self._connections[best] += 1
        return best

    def release(self, server: str) -> None:
        """Соединение завершено — освободить слот на сервере."""
        if self._connections.get(server, 0) > 0:
            self._connections[server] -= 1

    def stats(self) -> dict:
        """Текущее число активных соединений по серверам."""
        return dict(self._connections)


if __name__ == "__main__":
    lb = LoadBalancer(["api1", "api2", "api3"])

    # Пять запросов подряд без завершения соединений
    routed = [lb.route() for _ in range(5)]
    print("Маршрутизация 5 запросов:", routed)
    print("Активные соединения:", lb.stats())

    # Два запроса на api1 завершились — слоты освободились
    lb.release("api1")
    lb.release("api1")
    print("После release api1 x2:", lb.stats())

    # Следующий запрос должен уйти на наименее загруженный сервер
    nxt = lb.route()
    print("Следующий запрос ушёл на:", nxt)
    print("Итоговые соединения:", lb.stats())