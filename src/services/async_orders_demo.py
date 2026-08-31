import asyncio


async def enrich_order(order_id: str, amount: float, delay: float) -> dict:
    """Асинхронно «обогащает» заказ: имитирует обращение к сервису."""
    # Твой код здесь: подожди delay, верни dict с order_id, amount и with_vat
    await asyncio.sleep(delay)
    return {
        "order_id": order_id,
        "amount": amount,
        "with_vat": round(amount * 1.2, 2)
    }


async def process_orders(orders: list[tuple[str, float, float]]) -> list[dict]:
    """Обработай все заказы параллельно и сохрани исходный порядок."""
    # Твой код здесь
    return await asyncio.gather(*[enrich_order(order_id, amount, delay) for order_id, amount, delay in orders])


async def main() -> None:
    orders = [
        ("SFM-101", 1500.0, 0.03),
        ("SFM-102", 800.0, 0.01),
        ("SFM-103", 2400.0, 0.02),
    ]
    results = await process_orders(orders)
    for result in results:
        print(result)
    total_with_vat = sum(result["with_vat"] for result in results)
    print(f"Total amount with VAT: {total_with_vat}")


if __name__ == "__main__":
    asyncio.run(main())