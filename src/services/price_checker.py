import asyncio


async def check_supplier(name: str, product_id: int, delay: float, price: int):
    """Имитация запроса к поставщику"""
    await asyncio.sleep(delay)
    return {"supplier": name, "product_id": product_id, "price": price}

async def check_supplier_timeout(name: str, product_id: int):
    """Поставщик, который не отвечает"""
    await asyncio.sleep(10)
    raise TimeoutError(f"Поставщик {name} не отвечает")

async def find_best_price(product_id: int) -> dict:
    """Найти лучшую цену среди поставщиков"""
    # Твой код здесь
    suppliers = [
        ("Supplier1", product_id, 1.0, 100),
        ("Supplier2", product_id, 2.0, 150),
        ("Supplier3", product_id, 0.5, 120),

    ]
    tasks = [check_supplier(name, product_id, delay, price) for name, product_id, delay, price in suppliers]
    tasks.append(check_supplier_timeout("Supplier4", product_id))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Фильтрация успешных результатов
    valid_results = [r for r in results if not isinstance(r, Exception)]

    if not valid_results:
        return {"error": "Ни один поставщик не ответил"}

    # Поиск лучшей цены
    best = min(valid_results, key=lambda x: x["price"])
    return best


async def main():
    # Ограничиваем общее время ожидания
    try:
        result = await asyncio.wait_for(find_best_price(42), timeout=20.0)
        print(f"Лучшая цена: {result}")
    except asyncio.TimeoutError:
        print("Превышено время ожидания")

asyncio.run(main())