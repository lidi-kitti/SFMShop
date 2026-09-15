# Отрефакторенный код
def process_orders(orders):
    """Обрабатывает заказы со статусом 'new' и вычисляет итоговую сумму"""
    if not orders:
        return []
    
    result = []
    for order in orders:
        if order.get('status') != 'new':
            continue
        
        try:
            total = sum(
                item['price'] * item['quantity']
                for item in order.get('items', [])
            )
            order['total'] = total
            result.append(order)
        except (KeyError, TypeError) as e:
            print(f"Ошибка обработки заказа {order.get('id', 'unknown')}: {e}")
            continue
    
    return result

# Отчет об улучшениях:
# 1. Добавлена проверка на пустой список
# 2. Использовано генераторное выражение внутри sum() для более питоничного кода
# 3. Добавлена обработка ошибок через try/except
# 4. Использован .get() для безопасного доступа к словарю
# 5. Добавлена документация функции
# 6. Улучшена читаемость через continue вместо вложенных if