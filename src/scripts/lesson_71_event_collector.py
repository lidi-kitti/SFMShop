import logging
from collections import Counter


class EventCollector(logging.Handler):
    """Хендлер, который копит записи логов в памяти для анализа."""

    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


def main():
    logger = logging.getLogger(__name__)
    logger.addHandler(EventCollector())
    logger.error("Test error")
    logger.warning("Test warning")
    logger.info("Test info")
    logger.debug("Test debug")
    print(EventCollector().records)


if __name__ == "__main__":
    main()