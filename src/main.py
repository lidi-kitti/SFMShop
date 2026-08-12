# DISCOUNT_RATE = 0.1
# BASE_DISCOUNT = 0.1
# BASE_DELIVERY_COST = 100
# # ==================
# # УРОК 1: ПЕРЕМЕННЫЕ И СТРОКИ (STR)
# # ==================
#
# # Решение задачи от тимлида
# company_name = "SFMShop"
#
# welcome_message = "Добро пожаловать в " + company_name + "!"
# slogan = company_name + " - лучший выбор для покупок"
# email_subject = "Спасибо за покупку в " + company_name
#
# print(welcome_message)
# print(slogan)
# print(email_subject)
#
# # Практика: Задание 1 - Форматирование имен пользователей
# raw_name_1 = "ИВАН"
# raw_name_2 = "мария"
# raw_name_3 = "пЕТР"
#
# formatted_name_1 = raw_name_1.capitalize()
# formatted_name_2 = raw_name_2.capitalize()
# formatted_name_3 = raw_name_3.capitalize()
#
# print(formatted_name_1)
# print(formatted_name_2)
# print(formatted_name_3)
#
# # Практика: Задание 2 - Форматирование цены
# price = "1999"
#
# price_prefix = "от"
# currency = "руб."
#
# formatted_price = price_prefix + " " + price + " " + currency
# print(formatted_price)
#
# # Практика: Задание 3 - Расширенная обработка имен
# name_1 = "  ИВАН  "
# name_2 = "мария"
# name_3 = "  пЕТР  "
# name_4 = "АННА"
# name_5 = "  олег  "
#
# cleaned_name_1 = name_1.strip().capitalize()
# cleaned_name_2 = name_2.strip().capitalize()
# cleaned_name_3 = name_3.strip().capitalize()
# cleaned_name_4 = name_4.strip().capitalize()
# cleaned_name_5 = name_5.strip().capitalize()
#
# print(cleaned_name_1)
# print(cleaned_name_2)
# print(cleaned_name_3)
# print(cleaned_name_4)
# print(cleaned_name_5)
#
# # ==================
# # УРОК 2: ЧИСЛА (INT, FLOAT)
# # ==================
#
# # Урок 2: Решение задачи от тимлида - Конвертация валют
# exchange_rate = 75.5
#
# product_1_price_usd = 29.99
# product_2_price_usd = 49.99
# product_3_price_usd = 99.99
#
# # Конвертируем в рубли и округляем
# product_1_price_rub = round(product_1_price_usd * exchange_rate, 2)
# product_2_price_rub = round(product_2_price_usd * exchange_rate, 2)
# product_3_price_rub = round(product_3_price_usd * exchange_rate, 2)
#
# print(product_1_price_rub)
# print(product_2_price_rub)
# print(product_3_price_rub)
#
# # Практика: Задание 1 - Расчет итоговой стоимости заказа
# price_per_item = 1500.0
# quantity = 3
# discount = 0.1  # 10% скидка
#
# # Расчет итоговой стоимости
# final_price = price_per_item * quantity * (1 - discount)
# final_price_rounded = round(final_price, 2)
#
# print(final_price_rounded)
#
# # Практика: Задание 2 - Расширенный расчет стоимости заказов
# # Заказ 1: с обычной скидкой
# order_1_price = 2000.0
# order_1_quantity = 2
# order_1_discount = 0.15
#
# # Заказ 2: без скидки
# order_2_price = 3000.0
# order_2_quantity = 1
# order_2_discount = 0.0
#
# # Заказ 3: с большой суммой
# order_3_price = 5000.0
# order_3_quantity = 3
# order_3_discount = 0.2
#
# # Обработка заказа 1
# subtotal_1 = order_1_price * order_1_quantity
# discount_amount_1 = subtotal_1 * order_1_discount
# final_price_1 = round(subtotal_1 - discount_amount_1, 2)
#
# print("Заказ 1:")
# print("Исходная цена:", subtotal_1, "руб.")
# print("Размер скидки:", discount_amount_1, "руб.")
# print("Итоговая стоимость:", final_price_1, "руб.")
# print()
#
# # Обработка заказа 2
# subtotal_2 = order_2_price * order_2_quantity
# discount_amount_2 = subtotal_2 * order_2_discount
# final_price_2 = round(subtotal_2 - discount_amount_2, 2)
#
# print("Заказ 2:")
# print("Исходная цена:", subtotal_2, "руб.")
# print("Размер скидки:", discount_amount_2, "руб.")
# print("Итоговая стоимость:", final_price_2, "руб.")
# print()
#
# # Обработка заказа 3
# subtotal_3 = order_3_price * order_3_quantity
# discount_amount_3 = subtotal_3 * order_3_discount
# final_price_3 = round(subtotal_3 - discount_amount_3, 2)
#
# print("Заказ 3:")
# print("Исходная цена:", subtotal_3, "руб.")
# print("Размер скидки:", discount_amount_3, "руб.")
# print("Итоговая стоимость:", final_price_3, "руб.")
# print()
#
# # ==================
# # УРОК 3: УСЛОВНЫЕ ОПЕРАТОРЫ
# # ==================
#
# # Урок 3: Решение задачи от тимлида - Проверка условий заказа
# user_age = 20
# product_quantity = 5
#
# # Проверяем оба условия через and
# if user_age >= 18 and product_quantity > 0:
#     print("Заказ можно оформить")
# else:
#     # Определяем причину отказа
#     if user_age < 18:
#         print("Заказ нельзя оформить: пользователь несовершеннолетний")
#     if product_quantity <= 0:
#         print("Заказ нельзя оформить: товара нет на складе")
#
# # Практика: Задание 1 - Определение размера скидки
# order_total = 6000
#
# if order_total > 10000:
#     discount_rate = 0.15  # 15%
# elif order_total > 5000:
#     discount_rate = 0.10  # 10%
# else:
#     discount_rate = 0.05  # 5%
#
# print("Размер скидки:", discount_rate * 100, "%")
#
# # Практика: Задание 2 - Валидация и расчет стоимости заказа
# order_total = 6000
#
# # Проверяем, что сумма не отрицательная
# if order_total < 0:
#     print("Ошибка: сумма заказа не может быть отрицательной")
# else:
#     # Определяем размер скидки
#     if order_total > 10000:
#         discount_rate = 0.15
#     elif order_total > 5000:
#         discount_rate = 0.10
#     else:
#         discount_rate = 0.05
#
#     # Рассчитываем размер скидки в рублях
#     discount_amount = order_total * discount_rate
#
#     # Рассчитываем итоговую стоимость
#     final_price = round(order_total - discount_amount, 2)
#
#     # Выводим результаты
#     print("Исходная сумма:", order_total, "руб.")
#     print("Размер скидки:", discount_rate * 100, "%")
#     print("Размер скидки:", discount_amount, "руб.")
#     print("Итоговая стоимость:", final_price, "руб.")
#
# # ==================
# # УРОК 4: ЦИКЛЫ (FOR, WHILE)
# # ==================
#
# # Урок 4: Решение задачи от тимлида - Поиск заказов с суммой больше 5000
# order_1 = 3000
# order_2 = 6000
# order_3 = 4500
# order_4 = 8000
# order_5 = 2000
#
# # Создаем последовательность заказов через range
# for i in range(1, 6):
#     # Получаем значение заказа в зависимости от номера
#     if i == 1:
#         order_total = order_1
#     elif i == 2:
#         order_total = order_2
#     elif i == 3:
#         order_total = order_3
#     elif i == 4:
#         order_total = order_4
#     else:
#         order_total = order_5
#
#     # Проверяем условие и выводим
#     if order_total > 5000:
#         print("Заказ", i, ":", order_total)
#
# # Практика: Задание 1 - Поиск товаров с ценой больше 1000
# price_1 = 500
# price_2 = 1500
# price_3 = 800
# price_4 = 2000
# price_5 = 1200
#
# # Перебираем товары от 1 до 5
# for product_number in range(1, 6):
#     # Определяем цену товара по номеру
#     if product_number == 1:
#         price = price_1
#     elif product_number == 2:
#         price = price_2
#     elif product_number == 3:
#         price = price_3
#     elif product_number == 4:
#         price = price_4
#     else:
#         price = price_5
#
#     # Проверяем условие и выводим
#     if price > 1000:
#         print("Товар", product_number, ":", price, "руб.")
#
# # Практика: Задание 2 - Расширенная обработка товаров
# price_1 = 500
# price_2 = 1500
# price_3 = 800
# price_4 = 2000
# price_5 = 1200
#
# # Счетчик товаров с ценой больше 1000
# count = 0
#
# # Переменные для поиска максимальной цены
# max_price = 0
# max_price_product = 0
#
# print("Товары с ценой больше 1000:")
#
# # Перебираем товары от 1 до 5
# for product_number in range(1, 6):
#     # Определяем цену товара по номеру
#     if product_number == 1:
#         price = price_1
#     elif product_number == 2:
#         price = price_2
#     elif product_number == 3:
#         price = price_3
#     elif product_number == 4:
#         price = price_4
#     else:
#         price = price_5
#
#     # Проверяем условие и выводим
#     if price > 1000:
#         print("Товар", product_number, ":", price, "руб.")
#         count = count + 1
#
#     # Ищем максимальную цену
#     if price > max_price:
#         max_price = price
#         max_price_product = product_number
#
# print("Количество товаров с ценой больше 1000:", count)
# print("Товар с максимальной ценой: Товар", max_price_product, ", цена", max_price, "руб.")
#
# # ==================
# # УРОК 5: СПИСКИ (LIST)
# # ==================
#
# # Урок 5: Решение задачи от тимлида - Подсчет общей суммы заказов
# orders = [1500, 2300, 890, 4500, 1200]
#
# # Используем встроенные функции
# total = sum(orders)
# count = len(orders)
# average = total / count
#
# print("Общая сумма:", total)
# print("Средний чек:", average)
#
# # Практика: Задание 1 - Сортировка и поиск цен товаров
# prices = [1500, 2300, 890, 4500, 1200]
#
# # Сортируем по убыванию
# prices.sort(reverse=True)
#
# # Находим максимальную и минимальную цену
# max_price = max(prices)
# min_price = min(prices)
#
# # Выводим результаты
# print("Отсортированные цены:", prices)
# print("Максимальная цена:", max_price)
# print("Минимальная цена:", min_price)
#
# # Практика: Задание 2 - Управление корзиной покупок
# cart = []
#
# # Добавляем товары
# cart.append(["Ноутбук", 50000])
# cart.append(["Мышь", 1500])
# cart.append(["Клавиатура", 3000])
#
# print("Корзина после добавления товаров:", cart)
#
# # Удаляем товар
# cart.remove(["Мышь", 1500])
#
# print("Корзина после удаления:", cart)
#
# # Сортируем по названию
# cart.sort()
#
# print("Корзина после сортировки:", cart)
#
# # Ищем самый дорогой товар
# if len(cart) > 0:
#     max_price = 0
#     max_price_item = None
#
#     for item in cart:
#         price = item[1]  # Цена - второй элемент (индекс 1)
#         if price > max_price:
#             max_price = price
#             max_price_item = item
#
#     print("Самый дорогой товар:", max_price_item)
# else:
#     print("Корзина пустая")
#
# # ==================
# # УРОК 6: СЛОВАРИ (DICT) И МНОЖЕСТВА (SET)
# # ==================
#
# # Урок 6: Решение задачи от тимлида - Хранение данных пользователя и подсчет уникальных посетителей
# # Хранение данных пользователя в словаре
# user = {
#     "name": "Иван Иванов",
#     "email": "ivan@example.com",
#     "phone": "+7 999 123-45-67"
# }
#
# # Получение данных по ключу
# print("Имя:", user["name"])
# print("Email:", user["email"])
#
# # Подсчет уникальных посетителей через множество
# visitors = {"user_123", "user_456", "user_123", "user_789"}
# unique_count = len(visitors)
#
# print("Уникальных посетителей:", unique_count)
#
# # Практика: Задание 1 - Работа со словарем товара
# product = {
#     "name": "Ноутбук",
#     "price": 50000,
#     "quantity": 5
# }
#
# # Обновляем количество
# product["quantity"] = 10
#
# # Получаем ключи и значения
# keys = product.keys()
# values = product.values()
#
# print("Ключи словаря:", keys)
# print("Значения словаря:", values)
#
# # Практика: Задание 2 - Система хранения данных о пользователях и товарах
# # Словарь пользователей
# users = {
#     4:{
#         "name":"Ivan",
#         "email":"ivanivanov@mail.ru"
#     }
# }
#
# # Словарь товаров
# products = {
#     "Ноутбук": {
#         "price": 50000,
#         "category": "Электроника"
#     },
#     "Мышь": {
#         "price": 1500,
#         "category": "Аксессуары"
#     }
# }
#
# users[1]={
#     "name":"Иван",
#     "email":"ivan@test.com"
# }
# print(f"Пользователь добавлен: {users[1]}")
# if "Ноутбук" in products:
#     things = products["Ноутбук"]
#     price = things["price"]
#     print(f"Цена товара 'Ноутбук': {price} руб.")
# else:
#     print("Такого товара нет")
#
# set_products=set()
#
# set_products.add('user_123')
#
# if 'user_123' in set_products:
#     print("Посетитель 'user_123' был на сайте: True")
# else:
#     print("Посетитель 'user_123' не был на сайте: False")
#
#
#
# coordinates = (10,20)
# x,y=coordinates
# print("Координата x:", x)
# print("Координата y:", y)
# dictionary={coordinates:"Some place"}
# name_place=dictionary[coordinates]
# print("Название места:", name_place)
#
# dict_delivery = {
#     1:(55.7558,37.6173)
# }
# dict_delivery[1]=(55.7558,37.6173)
# dict_delivery[2]=(59.9343,30.3351)
# print("Координаты заказа 1:", dict_delivery[1])
# location = dict_delivery[1]
# latitude, longitude = location
# print("Широта:", latitude)
# print("Долгота:", longitude)
# id = 3
# if id in dict_delivery:
#     print(f"Координаты заказа {id}:", dict_delivery[id])
# else:
#     print(f"Координаты заказа {id}: Заказ не найден")
#
# def price_discount(price, discount_percent):
#     result = price*(1-discount_percent/100)
#     return result
#
# print("Цена товара 1 со скидкой:", price_discount(1000,10))
# print("Цена товара 2 со скидкой:", price_discount(5000,15))
#
# def calculate_order_total(price, quantity, discount):
#     result = (price * quantity) * (1 - discount)
#     return result
#
# def check_stock_availability(stock_quantity, required_quantity):
#     if stock_quantity >= required_quantity:
#         return True
#     else:
#         return False
#
# def format_order_info(order_id, total):
#     result = f"Заказ #{order_id}, Сумма: {total} руб."
#     return result
#
# result = check_stock_availability(10,3)
# print("Товар доступен:", result)
# if result:
#     summa = calculate_order_total(1000,3,0.1)
#     print("Информация о заказе:", format_order_info(1, summa))
#
#
# with open("data/products.txt", "r", encoding='utf-8') as file:
#     lines = file.readlines()
#
# # Обработка товаров и запись в новый файл
# with open("data/products_with_prices.txt", "w", encoding='utf-8') as file:
#     for line in lines:
#         product = line.strip()  # Удаляем символ переноса строки
#         product_with_price = product + " - 1000 руб.\n"
#         file.write(product_with_price)
#
# try:
#     with open("data/orders.txt", "r", encoding='utf-8') as file:
#         lines_orders = file.readlines()
# except FileNotFoundError:
#     print("Файл data/orders.txt не найден.")
#     lines_orders = []
#
# list_orders={}
# all_sum=0
# count_orders=0
# for line in lines_orders:
#     pos = line.find(":")
#     list_orders["id"] = line[:pos]
#     line1 = line[pos+1:]
#     pos1 = line1.find(":")
#     list_orders["sum"] = line1[:pos1]
#     list_orders["status"] = line1[pos1+1:].rstrip("\n")
#     if list_orders["status"]=="новый":
#         all_sum+=int(list_orders["sum"])
#         count_orders+=1
#         with open("data/processed_orders.txt", "w", encoding='utf-8') as file:
#             text = f"Обработано заказов: {count_orders}\nОбщая сумма: {all_sum} руб."
#             file.write(text)
#
#
# # Импорт своего модуля
# from utils.calculations import *
# from utils.validators import *
#
#
# # Использование функций
# discount_1 = calculate_discount(1000, 0.1)
# discount_2 = calculate_discount(5000, 0.15)
#
# print("Скидка для товара 1:", discount_1)
# print("Скидка для товара 2:", discount_2)
#
# user_age_check = validate_age(20)
# print('Возраст валиден:', user_age_check)
# user_email_check = validate_email("ivan@test.com")
# print('Email валиден:', user_email_check)
# if user_age_check and user_email_check:
#     discount = calculate_discount(1000, 0.1)
#     delivery = calculate_delivery(5)
#     price = calculate_final_price(1000, discount, delivery)
#     print('Итоговая стоимость заказа:', price, 'руб.')
#
# def calculate_price_with_discount(price):
#     result = price * (1 - DISCOUNT_RATE)
#     return result
#
# print('Цена со скидкой 10%:', calculate_price_with_discount(1000))
#
# DISCOUNT_RATE = 0.2
# print('Цена со скидкой 20%:', calculate_price_with_discount(1000))
#
#
# def calculate_order_price(price, quantity):
#     subtotal = price * quantity
#     discount = subtotal * BASE_DISCOUNT
#     total = subtotal - discount + BASE_DELIVERY_COST
#     return total
#
# def update_discount(new_discount):
#     global BASE_DISCOUNT
#     BASE_DISCOUNT = new_discount
#
# price1 = calculate_order_price(1000, 2)
# print('Стоимость заказа (скидка 10%):', price1)
# update_discount(0.15)
# price2 = calculate_order_price(1000, 2)
# print('Стоимость заказа (скидка 15%):', price2)
#
# def format_product_info(name, price, quantity):
#     res = f'Товар: {name}, Цена: {price} руб., Количество: {quantity}'
#     return res
#
# print("Информация о товаре:", format_product_info("Ноутбук", "50000", "10"))
# list_product = ["Ноутбук", "Мышь", "Клавиатура"]
# union_products = ", ".join(list_product)
# print(f"Товары: {union_products}")
#
# from datetime import datetime, timedelta
#
# date_now = datetime.now()
# formatted_date = date_now.strftime("%Y-%m-%d %H:%M:%S")
# print('Текущее время:', formatted_date)
# order_date = datetime(2024,1,15,10,00,00)
# print('Дата заказа:', order_date)
# delivery_date = datetime(2024,1,18,10,00,00)
# print('Дата доставки:', delivery_date)
# delta_days = (delivery_date-order_date).days
# print('Дней до доставки:', delta_days)
#
# def calculate_delivery_date(order_date, delivery_days):
#     return order_date + timedelta(days=delivery_days)
#
# def log_order_creation(order_id, order_time):
#     formatted_time = order_time.strftime("%Y-%m-%d %H:%M:%S")
#     return f"Заказ #{order_id} создан: {formatted_time}"
#
# order_date_new=datetime(2024,1,15,10,00,00)
# date_delivery_new = calculate_delivery_date(order_date_new, 3)
# print('Дата доставки:', date_delivery_new)
# log_order = log_order_creation(123, datetime.now())
# print('Заказ #123 создан:', log_order)
#
# import re
#
# def validate_email(email):
#     pattern = r".+@.+\..+"
#     res = re.match(pattern, email)
#     return res is not None
#
# email_1 = "ivan@example.com"
# email_2 = "invalid"
# email_3 = "test@"
# print("Email 'ivan@example.com' валиден:", validate_email(email_1))
# print("Email 'invalid' валиден:", validate_email(email_2))
# print("Email 'test@' валиден:", validate_email(email_3))
#
#
# def validate_email_regex(email):
#     pattern = r".+@.+\..+"
#     res = re.match(pattern, email)
#     return res is not None
#
# def validate_phone_regex(phone):
#     pattern = r"\+7[\s\d-]+"
#     res = re.match(pattern, phone)
#     return res is not None
#
# def clean_input(text):
#     pattern = r"[^\w\s.,!?-]"
#     clean_text = re.sub(pattern,"", text)
#     return clean_text
#
# def extract_email_from_text(text):
#     pattern = r"\S+@\S+\.\S+"
#     result = re.search(pattern, text)
#     if result:
#         email = result.group()
#         return email
#     else:
#         return None
#
# print("Email валиден:", validate_email_regex("ivan@test.com"))
# print("Телефон валиден:", validate_phone_regex("+7 999 123-45-67"))
# print("Очищенный текст:", clean_input("Заказ #123!!! Сумма: 5000 руб."))
# print("Извлеченный email:", extract_email_from_text("Свяжитесь с нами: support@example.com для помощи"))

# задача в конце базового модуля
#
# def load_orders_from_file(filename):
#     try:
#         with open(filename, 'r', encoding='utf-8') as f:
#             text = f.readlines()
#
#         list_orders=[]
#         for line in text:
#             cleaned_line =  line.strip()
#             if cleaned_line:
#                 list_orders.append(cleaned_line)
#         return list_orders
#     except FileNotFoundError as e:
#         print("Ошибка при чтении файла", e)
#         return []
#
#
# def calculate_order_total(price, discount_rate):
#     try:
#         result = price * (1 - discount_rate)
#         return round(result, 2)
#     except ValueError as e:
#         print("Ошибка при обработке данных", e)
#
#
# def get_discount_by_total(total):
#     try:
#         if total > 10000:
#             return 0.15
#         elif total > 5000:
#             return 0.1
#         elif total <=0:
#             return 0
#         else:
#             return 0.05
#     except ValueError as e:
#         print("Ошибка при обработке данных", e)
#
# def process_orders(orders_data):
#     processed = []
#     for order_row in orders_data:
#         try:
#             parts = order_row.split(":")
#             if len(parts)==4:
#                 order_id = parts[0].strip()
#                 order_sum = int(parts[1].strip())
#                 order_status = parts[2].strip()
#                 order_user = parts[3].strip()
#
#                 discount_rate = get_discount_by_total(order_sum)
#                 final_total = calculate_order_total(order_sum, discount_rate)
#
#                 processed.append({
#                     "order_id": order_id,
#                     "total": final_total,
#                     "status": order_status,
#                     "user": order_user
#                 })
#             else:
#                 print("Ошибка: неверный формат строки:", order_row)
#         except ValueError as e:
#             print("Ошибка при обработке данных", e)
#
#     return processed
#
# def analyze_orders(processed_orders):
#     try:
#         stats = {
#             "total_orders": 0,
#             "total_sum": 0,
#             "by_status": {},
#             "unique_users": set()
#         }
#         dict_status = {}
#         for order in processed_orders:
#             stats["total_orders"] += 1
#             stats["total_sum"] += order["total"]
#             status = order["status"]
#             dict_status[status] = dict_status.get(status, 0) + 1
#             stats["unique_users"].add(order["user"])
#         stats["by_status"] = dict_status
#         return stats
#     except ValueError as e:
#         print("Ошибка при обработке данных", e)
#


####### ООП

# from models.user import *
# from models.product import *
# from models.order import *
#
# user = User("Иван Иванов", "ivan@test.com")
# laptop = Product("Ноутбук", 50000, 1)
# mouse = Product("Мышь", 1500, 2)
#
# order = Order(user, [laptop, mouse])
# result = order.calculate_total()
# res_user = user.get_info()
# print(res_user)
# print("Общая стоимость заказа:", result)



# class Animal:
#     def make_sound():
#         return "Звук животного"
#
# class Dog(Animal):
#     def make_sound():
#         return "Гав-гав"
#
# class Cat(Animal):
#     def make_sound():
#         return "Мяу"
#
# dog = Dog
# cat = Cat
# print(dog.make_sound())
# print(cat.make_sound())
#
# from models.payment import *
# from models.product import *
# from models.order import *
# from models.user import *
#
# payments = [CardPayment(100000, "1234123412341234"),
#             CardPayment(200000, "1234123412341234"),
#             PayPalPayment(100000, "ivan@mail.ru"),
#             ]
#
# for pay in payments:
#     print(pay.process_payment())
#
#
# product_list = [Product("Мышь", 1500, 20),
#                 Product("Клавиатура", 3000, 15),
#                 Product("Ноутбук", 50000, 10)
#                 ]
# product_list.sort()
# for product in product_list:
#     print(product)
#
# order = Order("Иван", 1, 50000)
# print(order)
#
#
# ### try except
#
# def divide(a,b):
#     try:
#         if b == 0:
#             raise ZeroDivisionError("Ошибка: деление на ноль")
#         return print("Результат:", a/b)
#     except ZeroDivisionError as e:
#         print("Ошибка: деление на ноль!")
#     except TypeError as e:
#         print("Ошибка: неверный тип данных!")
#
# divide(10,2)
# divide(1,0)
# divide("kfkf",2)
#
# user = User("Иван Иванов", "test.com")
# print(user)
# order_list = Order("Иван", 1, -50000)
# print(order)
# product_list = [Product("Мышь", -1500, 20),
#                 Product("Клавиатура", 3000, 15),
#                 Product("Ноутбук", 50000, 10)
#                 ]
# product_list.sort()
# for product in product_list:
#     order.list_product(product.name)
#     print(product)
#
# ################
# from models.exceptions import *
#
# print("Задание: создание собственных исключений")
# try:
#     user = User("Иван Иванов", "test.com")
#     print(user)
#     order_list = Order("Иван", 1, -50000)
#     print(order)
#     product_list = [Product("Мышь", -1500, 20),
#                     Product("Клавиатура", 3000, 15),
#                     Product("Ноутбук", 50000, 10)
#                     ]
#     product_list.sort()
#     for product in product_list:
#         order.list_product(product.name)
#         print(product)
#
# except InsufficientStockError as e:
#     print("Ошибка склада:", e)
# except InvalidOrderError as e:
#     print("Ошибка при создании заказа:", e)
# except NegativePriceError as e:
#     print("Ошибка валидации:", e)
#
#
# except SFMShopException as e:
#     print("Ошибка проекта:", e)

### финальная задача ООП
# from models.product import Product
# from models.user import User
# from models.order import Order
# from models.payment import CardPayment, PayPalPayment
# from models.exceptions import ValidationError, SFMShopException
#
#
# def process_order_system():
#     # Создание пользователя
#     user = User("Иван", "ivan@test.com")
#
#     # Создание товаров
#     product1 = Product("Ноутбук", 50000, 2)
#     product2 = Product("Мышь", 1500, 3)
#
#     # Создание заказа
#     order = Order(user, [product1, product2])
#     print(order)
#
#     # Вычисление стоимости
#     total = order.calculate_total()
#     print("Общая стоимость заказа:", total)
#
#     # Создание платежей
#     payments = [
#         CardPayment(1000, "1234 5678 9012 3456"),
#         PayPalPayment(2000, "test@paypal.com")
#     ]
#
#     # Обработка платежей через полиморфизм
#     for payment in payments:
#         print(payment.process_payment())
#
#     # Сортировка товаров
#     sorted_products = sorted([product1, product2])
#     for product in sorted_products:
#         print(product)
#
#     # Обработка ошибок
#     try:
#         product1.set_price(-1000)
#     except ValidationError as e:
#         print("Ошибка валидации:", e)
#
#
# if __name__ == "__main__":
#     process_order_system()

# #Coomet for commit 1
# #Coomet for commit 2
# import psycopg2
# from psycopg2 import Error
# from database.connection import *
# from database.queries import *

# def main():
#     conn = connect_to_db()
#     if not conn:
#         return

#     try:
#         # Создать пользователя
#         create_user(conn, "Новый пользователь", "new1@test.com")

#         # Получить товары
#         products = get_all_products(conn)
#         print("Товары:", products)

#         # Получить пользователя
#         user = get_user_by_id(conn, 1)
#         print("Пользователь:", user)

#         # Статистика
#         stats = get_order_statistics(conn)
#         print("Статистика:", stats)

#         # Топ товары
#         top = get_top_products(conn, 5)
#         print("Топ товары:", top)

#         # История заказов
#         history = get_user_order_history(conn, 1)
#         print("История заказов:", history)

#     finally:
#         conn.close()

# if __name__ == "__main__":
#     main()

# Демонстрационный пример алгоритма (не записывается в SFMShop)
# import time

# class Product:
#     def __init__(self, id, name):
#         self.id = id
#         self.name = name

# # Создать большой список товаров
# products = [Product(i, f"Товар {i}") for i in range(10000)]

# def find_product_in_list(products, product_id):
#     for product in products:
#         if product.id == product_id:
#             return product
#     return None

# def find_product_in_dict(products_dict, product_id):
#     return products_dict.get(product_id)

# products_dict = {product.id: product for product in products}

# start = time.time()
# result_list = find_product_in_list(products, 5000)
# time_list = time.time() - start

# start = time.time()
# result_dict = find_product_in_dict(products_dict, 5000)
# time_dict = time.time() - start

# speedup = time_list / time_dict if time_dict > 0 else float("inf")

# print(f"Результат списка: {result_list.name if result_list else None}")
# print(f"Результат словаря: {result_dict.name if result_dict else None}")
# print(f"Результаты совпадают: {result_list is result_dict}")
# print(f"Время поиска в списке: {time_list:.6f} сек")
# print(f"Время поиска в словаре: {time_dict:.6f} сек")
# print(f"Ускорение: {speedup:.2f} раз")

# В файле src/main.py
# Демонстрационный пример алгоритма (не записывается в SFMShop)

# class Product:
#     def __init__(self, id, name, price):
#         self.id = id
#         self.name = name
#         self.price = price

#     def __str__(self):
#         return f"ID {self.id}: {self.name} — {self.price} руб."


# def binary_search_by_id(items, target):
#     """Бинарный поиск товара по ID (O(log n)). Верни товар или None."""
#     left = 0
#     right = len(items) - 1

#     while left <= right:
#         mid = (left + right) // 2
#         mid_id = items[mid].id
#         if mid_id == target:
#             return items[mid]
#         elif mid_id < target:
#             left = mid + 1
#         else:
#             right = mid - 1

#     return None


# def main():
#     products = [
#         Product(105, "Мышь", 1500),
#         Product(101, "Ноутбук", 50000),
#         Product(110, "Монитор", 18000),
#         Product(103, "Клавиатура", 3000),
#         Product(108, "Наушники", 7000),
#     ]
#     # Отсортируй по ID, выведи каталог, найди товары по ID 108, 110, 104
#     products.sort(key=lambda x: x.id)
#     for product in products:
#         print(product)
#     result = binary_search_by_id(products, 108)
#     print(result)
#     result = binary_search_by_id(products, 110)
#     print(result)
#     result = binary_search_by_id(products, 104)
#     print(result)
# if __name__ == "__main__":
#     main()

# Файл src/main.py — тестирование оптимизаций из utils.calculations
# from utils.calculations import benchmark_optimizations, create_test_products, create_products_catalog

# if __name__ == "__main__":
#     # Демонстрация каталога товаров (словарь O(1))
#     products = create_test_products(1000)
#     catalog = create_products_catalog(products)
#     print(f"Каталог создан: {len(catalog)} товаров")
#     print(f"Поиск ID=500: {catalog.get(500).name}")
#     print()

#     # Полный бенчмарк оптимизаций
#     benchmark_optimizations()

# В файле src/main.py — магические методы корзины
class Cart:
    def __init__(self):
        self.items = []  # список кортежей (название, цена)

    def __add__(self, item):
        self.items.append(item)
        return self

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def __call__(self):
        return sum(item[1] for item in self.items)


cart = Cart()
cart = cart + ("Ноутбук", 75000)
cart = cart + ("Мышь", 1200)
cart = cart + ("Клавиатура", 3500)

print(len(cart))
print(cart[0][0])
for name, price in cart:
    print(f"{name}: {price}")
print(cart())

# В файле src/main.py — полиморфизм скидок
from abc import ABC, abstractmethod


class Discount(ABC):
    """Абстрактный класс скидки"""

    @abstractmethod
    def apply(self, total_price):
        """Применить скидку к общей стоимости"""
        pass

    @abstractmethod
    def describe(self):
        pass


class PercentageDiscount(Discount):
    """Скидка в процентах"""

    def __init__(self, percentage):
        self.percentage = percentage

    def apply(self, total_price):
        return total_price * (1 - self.percentage / 100)

    def describe(self):
        return f"Скидка {self.percentage}%"


class FixedDiscount(Discount):
    """Фиксированная скидка"""

    def __init__(self, fixed_discount):
        self.fixed_discount = fixed_discount

    def apply(self, total_price):
        return total_price - self.fixed_discount

    def describe(self):
        return f"Скидка {self.fixed_discount} руб."


class DiscountCart:
    def __init__(self, discount: Discount):
        self.discount = discount
        self.items = []

    def add(self, name: str, price: float) -> None:
        self.items.append((name, price))

    def total(self) -> float:
        base = sum(price for _, price in self.items)
        return self.discount.apply(base)


def checkout(cart: DiscountCart) -> None:
    """Полиморфизм: работает с любой скидкой"""
    print(f"Товаров в корзине: {len(cart.items)}")
    print(f"Скидка: {cart.discount.describe()}")
    print(f"К оплате: {cart.total():.2f} руб.")


# Использование
cart1 = DiscountCart(PercentageDiscount(20))
cart1.add("Футболка", 1500)
cart1.add("Кепка", 1000)
checkout(cart1)

cart2 = DiscountCart(FixedDiscount(500))
cart2.add("Худи", 3000)
checkout(cart2)

# В файле src/main.py
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price  # присваивание пройдёт через сеттер

    @property
    def price(self):
        return self._price
    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("Цена не может быть отрицательной")
        self._price = value


product = Product("Ноутбук", 1000)
print(product.price)
product.price = 2000
print(product.price)
try:
    product.price = -100
except ValueError as e:
    print(e)
product.price = 2000
print(product.price)
