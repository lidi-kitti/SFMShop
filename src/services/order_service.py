from src.models.order import Order

def validate_order_data(order_data: dict):
    """Валидация данных заказа"""
    if not order_data.get("user_id"):
        raise ValueError("Нет user_id")
    if not order_data.get("items"):
        raise ValueError("Нет товаров")
    if len(order_data.get("items", [])) == 0:
        raise ValueError("Список товаров пуст")
    
    for item in order_data["items"]:
        if not item.get("price"):
            raise ValueError("Нет цены товара")
        if not item.get("quantity"):
            raise ValueError("Нет количества")
        if item["price"] < 0:
            raise ValueError("Цена не может быть отрицательной")
        if item["quantity"] <= 0:
            raise ValueError("Количество должно быть положительным")

def calculate_order_total(items: list):
    """Расчет общей стоимости заказа"""
    total = 0
    for item in items:
        total += item["price"] * item["quantity"]
    return total

def calculate_discount(total: float):
    """Расчет скидки"""
    if total > 10000:
        return 0.15
    elif total > 5000:
        return 0.10
    elif total > 1000:
        return 0.05
    return 0

def check_user_balance(user_id, required_amount):
    """Проверка баланса пользователя"""
    user_balance = get_user_balance(user_id)
    if user_balance < required_amount:
        raise ValueError("Недостаточно средств")
    return True

def create_order(user_id, items, total):
    """Создание заказа"""
    order_id = save_order_to_db(user_id, items, total)
    return order_id

def notify_user(user_id, order_id, total):
    """Отправка уведомления"""
    user_email = get_user_email(user_id)
    send_email(user_email, f"Заказ #{order_id} оформлен на сумму {total}")

def log_order_processing(order_id, user_id, total):
    """Логирование обработки заказа"""
    print(f"Заказ {order_id} обработан: пользователь {user_id}, сумма {total}")

def process_order(order_data):
    """Основная функция обработки заказа - координирует остальные"""
    # Валидация
    validate_order_data(order_data)
    
    # Расчет стоимости
    total = calculate_order_total(order_data["items"])
    
    # Применение скидки
    discount_rate = calculate_discount(total)
    final_total = total * (1 - discount_rate)
    
    # Проверка баланса
    check_user_balance(order_data["user_id"], final_total)
    
    # Создание заказа
    order_id = create_order(order_data["user_id"], order_data["items"], final_total)
    
    # Уведомление
    notify_user(order_data["user_id"], order_id, final_total)
    
    # Логирование
    log_order_processing(order_id, order_data["user_id"], final_total)
    
    return {
        "order_id": order_id,
        "total": final_total,
        "discount": discount_rate
    }

def save_order_to_db(user_id, items, total):
    """Сохранение заказа в базу данных"""
    return f"order_{user_id}_{total}"

def get_user_email(user_id):
    """Получение email пользователя"""
    return f"user_{user_id}@example.com"

def send_email(email, message):
    """Отправка email"""
    print(f"Отправка email на {email}: {message}")

def get_user_balance(user_id):
    """Получение баланса пользователя"""
    return 10000