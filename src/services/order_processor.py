import asyncio


async def validate_order(order_id: int) -> dict:
    """Валидация заказа"""
    await asyncio.sleep(1)
    return {"order_id": order_id, "valid": True}


async def reserve_items(order_id: int) -> dict:
    """Резервирование товаров"""
    await asyncio.sleep(1.5)
    return {"order_id": order_id, "reserved": True}


async def verify_address(order_id: int) -> dict:
    """Проверка адреса доставки"""
    await asyncio.sleep(0.5)
    return {"order_id": order_id, "address_valid": True}


async def process_order_tg(order_id: int) -> dict:
    """Обработка заказа через TaskGroup"""
    try:    
        async with asyncio.TaskGroup() as tg:
            validate_task = tg.create_task(validate_order(order_id))
            reserve_task = tg.create_task(reserve_items(order_id))
            verify_task = tg.create_task(verify_address(order_id))
            await asyncio.gather(validate_task, reserve_task, verify_task)
        return {
            "order_id": order_id,
            "valid": validate_task.result()["valid"],
            "reserved": reserve_task.result()["reserved"],
            "address_valid": verify_task.result()["address_valid"],
            "status": "ready"
        }
    except* ValueError as eg:
        errors = [str(e) for e in eg.exceptions]
        result = {"order_id": order_id, "status": "validation_error", "errors": errors}
    
    except* ConnectionError as eg:
        errors = [str(e) for e in eg.exceptions]
        result = {"order_id": order_id, "status": "service_error", "errors": errors}
    
    return result

async def main():
    order_ids = [1, 2, 3, 4, 5]
    for order_id in order_ids:
        result = await process_order_tg(order_id)
        print(result)

asyncio.run(main())