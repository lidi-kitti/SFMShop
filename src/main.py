# ==================
# УРОК 1: ПЕРЕМЕННЫЕ И СТРОКИ (STR)
# ==================

# Решение задачи от тимлида
company_name = "SFMShop"

welcome_message = "Добро пожаловать в " + company_name + "!"
slogan = company_name + " - лучший выбор для покупок"
email_subject = "Спасибо за покупку в " + company_name

print(welcome_message)
print(slogan)
print(email_subject)

# Практика: Задание 1 - Форматирование имен пользователей
raw_name_1 = "ИВАН"
raw_name_2 = "мария"
raw_name_3 = "пЕТР"

formatted_name_1 = raw_name_1.capitalize()
formatted_name_2 = raw_name_2.capitalize()
formatted_name_3 = raw_name_3.capitalize()

print(formatted_name_1)
print(formatted_name_2)
print(formatted_name_3)

# Практика: Задание 2 - Форматирование цены
price = "1999"

price_prefix = "от"
currency = "руб."

formatted_price = price_prefix + " " + price + " " + currency
print(formatted_price)

# Практика: Задание 3 - Расширенная обработка имен
name_1 = "  ИВАН  "
name_2 = "мария"
name_3 = "  пЕТР  "
name_4 = "АННА"
name_5 = "  олег  "

cleaned_name_1 = name_1.strip().capitalize()
cleaned_name_2 = name_2.strip().capitalize()
cleaned_name_3 = name_3.strip().capitalize()
cleaned_name_4 = name_4.strip().capitalize()
cleaned_name_5 = name_5.strip().capitalize()

print(cleaned_name_1)
print(cleaned_name_2)
print(cleaned_name_3)
print(cleaned_name_4)
print(cleaned_name_5)

# ==================
# УРОК 2: ЧИСЛА (INT, FLOAT)
# ==================

# Решение задачи от тимлида - Конвертация валют
exchange_rate = 75.5  # Курс валюты

product_1_price_usd = 29.99
product_2_price_usd = 49.99
product_3_price_usd = 99.99

# Конвертируем в рубли и округляем
product_1_price_rub = round(product_1_price_usd * exchange_rate, 2)
product_2_price_rub = round(product_2_price_usd * exchange_rate, 2)
product_3_price_rub = round(product_3_price_usd * exchange_rate, 2)

print(product_1_price_rub)  # 2264.24
print(product_2_price_rub)  # 3774.25
print(product_3_price_rub)  # 7549.24

# Практика: Задание 1 - Расчет итоговой стоимости заказа
price_per_item = 1500.0
quantity = 3
discount = 0.1  # 10% скидка

# Расчет итоговой стоимости
final_price = price_per_item * quantity * (1 - discount)
final_price_rounded = round(final_price, 2)

print(final_price_rounded)

# Практика: Задание 2 - Сдача и купюры
paid = 5000  # сколько дал покупатель
cost = 3750  # стоимость заказа

change = paid - cost
notes = change // 500
rest = change % 500

print(f"Сдача: {change} руб; купюр по 500: {notes}, остаток: {rest} руб.")

# ==================
# УРОК 3: УСЛОВНЫЕ ОПЕРАТОРЫ
# ==================

# Решение задачи от тимлида - Проверка условий заказа
user_age = 20
product_quantity = 5

# Проверяем оба условия через and
if user_age >= 18 and product_quantity > 0:
    print("Заказ можно оформить")
else:
    # Определяем причину отказа
    if user_age < 18:
        print("Заказ нельзя оформить: пользователь несовершеннолетний")
    if product_quantity <= 0:
        print("Заказ нельзя оформить: товара нет на складе")

# Практика: Задание 1 - Определение размера скидки
order_total = 6000

if order_total > 10000:
    discount_rate = 0.15  # 15%
elif order_total > 5000:
    discount_rate = 0.10  # 10%
else:
    discount_rate = 0.05  # 5%

print("Размер скидки: " + str(discount_rate * 100) + "%")

# Практика: Задание 2 - Доступ пользователя
user_age = 17
user_balance = 500
order_total = 1000
requested_qty = 3
in_stock = 5

if user_age < 18:
    print("Отказ: пользователь несовершеннолетний")
elif user_balance < order_total:
    print("Отказ: недостаточно средств")
elif requested_qty > in_stock:
    print("Отказ: товара недостаточно на складе")
else:
    print("Заказ можно оформить")

# Практика: Задание 3 - Расчёт стоимости доставки
order_total = 3500
city = "Казань"

if order_total > 5000:
    delivery_cost = 0
elif city == "Москва" or city == "Санкт-Петербург":
    delivery_cost = 300
else:
    delivery_cost = 500

print("Стоимость доставки: " + str(delivery_cost) + " руб.")

# ==================
# УРОК 4: СПИСКИ (LIST)
# ==================

# Решение задачи от тимлида - Подсчет общей суммы заказов
orders = [1500, 2300, 890, 4500, 1200]

# Используем встроенные функции
total = sum(orders)
count = len(orders)
average = total / count

print("Общая сумма:", total)
print("Средний чек:", average)

# Практика: Задание 1 - Сортировка и поиск цен товаров
prices = [1500, 2300, 890, 4500, 1200]

# Сортируем по убыванию
prices.sort(reverse=True)

# Находим максимальную и минимальную цену
max_price = max(prices)
min_price = min(prices)

# Выводим результаты
print("Отсортированные цены:", prices)
print("Максимальная цена:", max_price)
print("Минимальная цена:", min_price)

# Практика: Задание 2 - Копирование списка заказов
orders = [1500, 2300, 890]

# Создаем копию для архива
archive = orders.copy()

# Добавляем новый заказ в оригинал
orders.append(4500)

# Проверяем, что архив не изменился
print("Текущие заказы:", orders)
print("Архив заказов:", archive)

# ==================
# УРОК 5: ЦИКЛЫ (FOR, WHILE)
# ==================

# Решение задачи от тимлида - Поиск заказов с суммой больше 5000
orders = [3000, 6000, 4500, 8000, 2000]

for order in orders:
    if order > 5000:
        print("Большой заказ:", order)

# Практика: Задание 1 - Поиск товаров с ценой больше 1000
prices = [500, 1500, 800, 2000, 1200]

# Перебираем индексы товаров: 0, 1, 2, 3, 4
for i in range(len(prices)):
    price = prices[i]
    # Проверяем условие и выводим (номер товара = индекс + 1)
    if price > 1000:
        print("Товар " + str(i + 1) + ": " + str(price) + " руб.")

# Практика: Задание 2 - Сумма корзины со скидкой
prices = [500, 1500, 800, 2000, 1200]

total = 0
for price in prices:
    total += price

if total > 5000:
    total = total * 0.9

print(f"Итоговая сумма: {total} руб.")

# ==================
# УРОК 6: СЛОВАРИ (DICT) И МНОЖЕСТВА (SET)
# ==================

# Решение задачи от тимлида - Данные пользователя в словаре и уникальные посетители
# Хранение данных пользователя в словаре
user = {
    "name": "Иван Иванов",
    "email": "ivan@example.ru",
    "phone": "+7 999 123-45-67"
    }

# Получение данных по ключу
print("Имя:", user["name"])
print("Email:", user["email"])

# Подсчет уникальных посетителей через множество
visitors = {"user_123", "user_456", "user_123", "user_789"}
unique_count = len(visitors)

print("Уникальных посетителей:", unique_count)

# Практика: Задание 1 - Работа со словарем товара
product = {
    "name": "Ноутбук",
    "price": 50000,
    "quantity": 5
    }

# Обновляем количество
product["quantity"] = 10

# Получаем ключи и значения
keys = product.keys()
values = product.values()

print("Ключи словаря:", keys)
print("Значения словаря:", values)

# Практика: Задание 2 - Генератор словаря из списка товаров
catalog = [["Ноутбук", 50000], ["Мышь", 1500], ["Клавиатура", 3000]]

# Создаем словарь через генератор
prices = {item[0]: item[1] for item in catalog}

print("Словарь цен:", prices)
print("Цена мыши:", prices.get("Мышь", 0))

# ==================
# УРОК 7: КОРТЕЖИ (TUPLE)
# ==================

# Решение задачи от тимлида - Хранение размеров товара в кортеже
# Хранение размеров в кортеже
dimensions = (30, 20, 15)

# Распаковка для расчета объема
length, width, height = dimensions
volume = length * width * height

print("Размеры товара:", dimensions)
print("Объем упаковки:", volume)

# Практика: Задание 1 - Работа с кортежами
# Создание кортежа с координатами
coordinates = (10, 20)

# Распаковка кортежа
x, y = coordinates

print("Координата x:", x)
print("Координата y:", y)

# Использование кортежа как ключа в словаре
locations = {
    (10, 20): "Офис",
    (30, 40): "Склад"
    }

# Получение названия места по координатам
location_name = locations[coordinates]
print("Название места:", location_name)

# Практика: Задание 2 - Распаковка координат склада
warehouse = (55, 37, "Москва")

lat, lon, city = warehouse

print(f"Склад в городе {city}: широта {lat}, долгота {lon}")

# ==================
# УРОК 8: ФУНКЦИИ
# ==================

# Решение задачи от тимлида - Валидация email и гибкое логирование
def validate_email(email):
    if "@" in email and "." in email:
        return True
    else:
        return False

# Проверка всех email через функцию
email_1 = "ivan@example.ru"
email_2 = "petr@test"
email_3 = "invalid-email"

result_1 = validate_email(email_1)
result_2 = validate_email(email_2)
result_3 = validate_email(email_3)

print("Email 1 валиден:", result_1)
print("Email 2 валиден:", result_2)
print("Email 3 валиден:", result_3)


def log_message(level, *args):
    # level - обязательный параметр (уровень лога)
    # args - любое количество данных для записи
    parts = []
    for item in args:
        parts.append(str(item))
    message = "[" + level + "] " + " ".join(parts)
    print(message)

# Разные варианты использования
log_message("INFO", "Пользователь зарегистрирован")
log_message("ERROR", "Ошибка валидации", "email", "petr@test")
log_message("DEBUG", "Проверка email", "ivan@example.ru", True)

# Практика: Задание 1 - Функция расчета цены со скидкой
def calculate_price_with_discount(price, discount_percent):
    final_price = price * (1 - discount_percent / 100)
    return final_price

# Вызов функции для разных товаров
price_1 = calculate_price_with_discount(1000, 10)
price_2 = calculate_price_with_discount(5000, 15)

print("Цена товара 1 со скидкой:", price_1)
print("Цена товара 2 со скидкой:", price_2)

# Практика: Задание 2 - Функция суммирования с *args
def sum_all(*args):
    total = 0
    for num in args:
        total = total + num
    return total

# Вызов с разным количеством аргументов
result_1 = sum_all(100, 200)
result_2 = sum_all(100, 200, 300, 400, 500)
result_3 = sum_all()

print("Сумма двух чисел:", result_1)
print("Сумма пяти чисел:", result_2)
print("Сумма без аргументов:", result_3)

# Практика: Задание 3 - Функция создания описания товара с **kwargs
def describe_product(name, **kwargs):
    parts = []
    for key in kwargs:
        parts.append(key + ": " + str(kwargs[key]))
    description = name + " (" + ", ".join(parts) + ")"
    return description

# Вызов с разным набором характеристик
info_1 = describe_product("Ноутбук", цена=50000, бренд="Lenovo", вес=2.1)
info_2 = describe_product("Мышь", цвет="черный")
info_3 = describe_product("Клавиатура")

print(info_1)
print(info_2)
print(info_3)

# ==================
# УРОК 9: РАБОТА С ФАЙЛАМИ
# ==================

# Решение задачи от тимлида - Сохранение лога ошибок
error_message = "Ошибка: товар не найден на складе\n"

# Использование контекстного менеджера и режима 'a'
with open("src/data/errors.log", "a", encoding="utf-8") as file:
    file.write(error_message)
# Файл автоматически закрывается

# Практика: Задание 1 - Чтение и запись товаров
# Чтение товаров из файла
with open("src/data/products.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# Обработка товаров и запись в новый файл
with open("src/data/products_with_prices.txt", "w", encoding="utf-8") as file:
    for line in lines:
        product = line.strip()  # Удаляем символ переноса строки
        product_with_price = product + " - 1000 руб.\n"
        file.write(product_with_price)

# Практика: Задание 2 - Подсчёт заказов в файле
with open("src/data/orders.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

orders = [line for line in lines if line.strip()]

print(f"Заказов в файле: {len(orders)}")

# ==================
# УРОК 10: ИМПОРТИРОВАНИЕ МОДУЛЕЙ, СОЗДАНИЕ СВОИХ МОДУЛЕЙ
# ==================

# Решение задачи от тимлида - Генерация промо-кода через модуль random
import random

promo_number = random.randint(100000, 999999)
promo_code = "PROMO" + str(promo_number)

print("Промо-код:", promo_code)

# Практика: Задание 1 - Создание модуля расчетов
from utils.calculations import calculate_discount

discount_1 = calculate_discount(1000, 0.1)
discount_2 = calculate_discount(5000, 0.15)

print("Скидка для товара 1:", discount_1)
print("Скидка для товара 2:", discount_2)

# Практика: Задание 2 - Функция скидки в отдельном модуле
# from utils.discounts import apply_discount

# result = discounts.apply_discount(2000, 25)
# print(f"Цена со скидкой: {result} руб.")

# ==================
# УРОК 11: ОБЛАСТИ ВИДИМОСТИ ПЕРЕМЕННЫХ
# ==================

# Решение задачи от тимлида - Глобальная константа стоимости доставки
# Глобальная константа определена в начале секции, до использования
BASE_DELIVERY_COST = 100

def calculate_order_total(price, quantity):
    # Используем глобальную константу (читаем, не изменяем)
    total = price * quantity + BASE_DELIVERY_COST
    return total

result = calculate_order_total(1000, 3)
print("Итого:", result)

# Практика: Задание 1 - Работа с глобальными переменными
# Глобальная переменная
DISCOUNT_RATE = 0.1

def calculate_price_with_discount(price):
    final_price = price * (1 - DISCOUNT_RATE)
    return final_price

# Первый вызов
price_1 = calculate_price_with_discount(1000)
print("Цена со скидкой 10%:", price_1)

# Изменение глобальной переменной
DISCOUNT_RATE = 0.2

# Второй вызов
price_2 = calculate_price_with_discount(1000)
print("Цена со скидкой 20%:", price_2)

# Практика: Задание 2 - Счётчик обработанных заказов
processed = 0

def handle_order():
    global processed
    processed += 1

handle_order()
handle_order()
handle_order()

print(f"Обработано заказов: {processed}")

# ==================
# УРОК 12: F-СТРОКИ, МЕТОДЫ СТРОК, ОТЛАДКА
# ==================

# Решение задачи от тимлида - Форматирование сообщения для лога через f-строку
order_id = 123
order_total = 5000
order_status = "новый"

# Использование f-строки вместо сложной конкатенации
message = f"Заказ #{order_id}, Сумма: {order_total} руб., Статус: {order_status}"
print(message)

# Практика: Задание 1 - Форматирование информации о товаре
def format_product_info(name, price, quantity):
    info = f"Товар: {name}, Цена: {price} руб., Количество: {quantity}"
    return info

# Использование функции
product_info = format_product_info("Ноутбук", 50000, 10)
print("Информация о товаре:", product_info)

# Обработка списка товаров
products = ["Ноутбук", "Мышь", "Клавиатура"]
products_string = ", ".join(products)
print(f"Товары: {products_string}")

# Практика: Задание 2 - Форматирование цены до копеек
price = 1234.5

print(f"Цена: {price:.2f} руб.")

# ==================
# УРОК 13: РАБОТА С ДАТАМИ И ВРЕМЕНЕМ
# ==================

# Решение задачи от тимлида - Расчет даты доставки через datetime и timedelta
from datetime import datetime, timedelta

# Создание объекта datetime
order_date = datetime(2024, 1, 15, 10, 0, 0)

# Расчет даты доставки
delivery_days = 3
delivery_date = order_date + timedelta(days=delivery_days)

print("Дата заказа:", order_date)
print("Дата доставки:", delivery_date)

# Практика: Задание 1 - Работа с датами
# Текущая дата и время
current_time = datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
print("Текущее время:", formatted_time)

# Даты заказа и доставки
order_date = datetime(2024, 1, 15, 10, 0, 0)
delivery_date = datetime(2024, 1, 18, 10, 0, 0)

print("Дата заказа:", order_date.strftime("%Y-%m-%d %H:%M:%S"))
print("Дата доставки:", delivery_date.strftime("%Y-%m-%d %H:%M:%S"))

# Разница между датами
difference = delivery_date - order_date
days = difference.days
print("Дней до доставки:", days)

# Практика: Задание 2 - Сколько дней до дедлайна
from datetime import date

start = date(2026, 12, 1)
deadline = date(2026, 12, 31)

delta = deadline - start
print(f"До дедлайна: {delta.days} дней")

# ==================
# УРОК 14: РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ
# ==================

# Решение задачи от тимлида - Надежная валидация email и телефона через regex
import re


def validate_email(email):
    pattern = r"[^@\s]+@[^@\s]+\.[^@\s]+"
    result = re.fullmatch(pattern, email)
    return result is not None


def validate_phone(phone):
    pattern = r"\+7[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}"
    result = re.fullmatch(pattern, phone)
    return result is not None

email = "ivan@example.ru"
phone = "+7 999 123-45-67"

print("Email валиден:", validate_email(email))
print("Телефон валиден:", validate_phone(phone))

# Практика: Задание 1 - Валидация email через регулярное выражение
def validate_email(email):
    pattern = r"[^@\s]+@[^@\s]+\.[^@\s]+"
    result = re.fullmatch(pattern, email)
    return result is not None

# Проверка разных email
email1 = "ivan@example.ru"
email2 = "invalid"
email3 = "test@"

print("Email '" + email1 + "' валиден:", validate_email(email1))
print("Email '" + email2 + "' валиден:", validate_email(email2))
print("Email '" + email3 + "' валиден:", validate_email(email3))

# Практика: Задание 2 - Извлечь все цены из текста
text = "Ноутбук 50000, мышь 800, клавиатура 1500"

prices = re.findall(r"\d+", text)
print(f"Найдены цены: {prices}")

# ==================
# УРОК 15: КЛАССЫ (ООП)
# ==================

# Менторское задание: классы Product, User, Order используются вместе
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "models"))
from models.product import Product
from models.user import User
from models.order import Order

# Создание объектов
user = User("Иван Иванов", "ivan@test.ru")
laptop = Product("Ноутбук", 50000, 1)
mouse = Product("Мышь", 1500, 2)

# Создание заказа
products = [laptop, mouse]
order = Order(user, products)

# Использование методов
print(user.get_info())
print("Общая стоимость заказа:", order.calculate_total())

# ==================
# УРОК 16: ПРИНЦИПЫ ООП
# ==================

# Решение задачи от тимлида - иерархия платежей
# (наследование, инкапсуляция, полиморфизм, абстракция)
class Payment:
    def __init__(self, amount):
        self.amount = amount

    def process_payment(self):
        raise NotImplementedError("Метод должен быть переопределен")


class CardPayment(Payment):
    def __init__(self, amount, card_number):
        super().__init__(amount)
        self.__card_number = card_number  # Приватный атрибут

    def process_payment(self):
        # Доступ к приватному атрибуту только изнутри класса
        masked_card = "**** " + self.__card_number[-4:]
        return "Оплата картой " + masked_card + ": " + str(self.amount) + " руб."


class PayPalPayment(Payment):
    def __init__(self, amount, email):
        super().__init__(amount)
        self._email = email  # Защищенный атрибут

    def process_payment(self):
        return "Оплата PayPal (" + self._email + "): " + str(self.amount) + " руб."


# Использование полиморфизма: единый интерфейс для разных типов платежей
payments = [
    CardPayment(1000, "1234 5678 9012 3456"),
    PayPalPayment(2000, "user@paypal.com"),
]

for payment in payments:
    print(payment.process_payment())

# Практика: Задание 1 - Наследование (Animal, Dog, Cat)
class Animal:
    def make_sound(self):
        return "Звук животного"


class Dog(Animal):
    def make_sound(self):
        return "Гав-гав"


class Cat(Animal):
    def make_sound(self):
        return "Мяу"


dog = Dog()
cat = Cat()

print(dog.make_sound())
print(cat.make_sound())

# Практика: Задание 2 - Полиморфизм и инкапсуляция (товары SFMShop)
class Product:
    def __init__(self, name, price):
        self.name = name
        self._price = price  # защищённый атрибут

    def final_price(self):
        return self._price


class DiscountProduct(Product):
    def __init__(self, name, price, discount):
        super().__init__(name, price)
        self.__discount = discount  # приватный атрибут

    def final_price(self):
        return self._price * (1 - self.__discount)


class GiftProduct(Product):
    def final_price(self):
        return 0


products = [
    Product("Кружка", 500),
    DiscountProduct("Футболка", 1000, 0.2),
    GiftProduct("Открытка", 300),
]

for product in products:
    print(product.name + ": " + str(product.final_price()) + " руб.")

# ==================
# УРОК 17: МАГИЧЕСКИЕ МЕТОДЫ
# ==================

# Решение задачи от тимлида - читаемый вывод и сравнение товаров
# В src/models/product.py добавлены __str__, __repr__, __lt__, __eq__
from models.product import Product

laptop = Product("Ноутбук", 50000, 10)
print(laptop)  # Товар: Ноутбук, Цена: 50000 руб., Количество: 10

products = [
    Product("Ноутбук", 50000, 10),
    Product("Мышь", 1500, 20),
    Product("Клавиатура", 3000, 15),
]
products.sort()  # сортировка по цене через __lt__
for product in products:
    print(product)

# Практика: Задание 2 - Корзина с __len__ и __add__
class Cart:
    def __init__(self, owner, items):
        self.owner = owner
        self.items = items

    def __len__(self):
        return len(self.items)

    def __add__(self, other):
        return Cart(self.owner, self.items + other.items)

    def __str__(self):
        return "Корзина " + self.owner + ": " + str(len(self)) + " товаров на " + str(sum(self.items)) + " руб."

cart1 = Cart("Иван", [50000, 1500])
cart2 = Cart("Иван", [3000, 2500])

print(len(cart1))
merged = cart1 + cart2
print(len(merged))
print(merged)

# ==================
# УРОК 18: ОБРАБОТКА ИСКЛЮЧЕНИЙ (TRY/EXCEPT, RAISE)
# ==================

# Решение задачи от тимлида - валидация через raise и обработка через try/except
class Product:
    def __init__(self, name, price, quantity):
        self.name = name

        # Валидация: проверяем данные и выбрасываем исключение вызывающему коду
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        self.price = price

        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        self.quantity = quantity

    def apply_discount(self, discount_percent):
        if discount_percent == 0:
            raise ValueError("Процент скидки не может быть равен нулю")
        new_price = self.price / (discount_percent / 100)
        return new_price


# Использование - вызывающий код обрабатывает исключения
try:
    product = Product("Ноутбук", -50000, 10)
except ValueError as e:
    print("Ошибка при создании товара:", e)
    product = Product("Ноутбук", 0, 10)  # Создаем с корректными данными

try:
    result = product.apply_discount(0)
    print("Цена со скидкой:", result)
except ValueError as e:
    print("Ошибка при применении скидки:", e)

# Практика: Задание 1 - Обработка ошибок деления
def divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("Ошибка: деление на ноль!")
        return None
    except TypeError:
        print("Ошибка: неверный тип данных!")
        return None

# Тестирование
print("Результат:", divide(10, 2))
print(divide(10, 0))
print(divide("10", 2))

# Практика: Задание 2 - Резервирование товара со складскими исключениями
class OutOfStockError(Exception):
    pass


class Order:
    def __init__(self, product_name, stock):
        self.product_name = product_name
        self.stock = stock

    def reserve(self, quantity):
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        if quantity > self.stock:
            raise OutOfStockError(
                f"Недостаточно товара: запрошено {quantity}, в наличии {self.stock}"
            )
        self.stock -= quantity
        return self.stock


order = Order("Ноутбук", 5)

requests = [3, 10, 0]
for qty in requests:
    try:
        remaining = order.reserve(qty)
        print(f"Зарезервировано {qty}, осталось {remaining}")
    except OutOfStockError as e:
        print("Нет на складе:", e)
    except ValueError as e:
        print("Ошибка ввода:", e)

# Менторское задание - Обработка исключений в классах
# Классы валидируют данные и бросают исключения через raise,
# вызывающий код обрабатывает их через try/except
from models.product import Product
from models.user import User
from models.order import Order
from models.exceptions import NegativePriceError

try:
    product = Product("Ноутбук", -50000, 10)
except (ValueError, NegativePriceError) as e:
    print("Ошибка при создании товара:", e)
    product = Product("Ноутбук", 0, 10)

try:
    user = User("Иван", "неверный_email")
except ValueError as e:
    print("Ошибка при создании пользователя:", e)
    user = User("Иван", "default@example.ru")

try:
    order = Order(user, [])
    order.add_product(Product("Несуществующий товар", 1000, 1))
except KeyError as e:
    print("Ошибка при создании заказа:", e.args[0])

# ==================
# УРОК 19: СОЗДАНИЕ СОБСТВЕННЫХ ИСКЛЮЧЕНИЙ
# ==================

# Практика: Задание 2 - Иерархия собственных исключений склада
class SFMShopException(Exception):
    """Базовое исключение проекта SFMShop"""
    pass


class InsufficientStockError(SFMShopException):
    """Товара недостаточно на складе"""
    pass


class InvalidQuantityError(SFMShopException):
    """Некорректное количество товара"""
    pass


class Product:
    def __init__(self, name, stock):
        self.name = name
        self.stock = stock

    def sell(self, amount):
        if amount <= 0:
            raise InvalidQuantityError(
                f"Количество должно быть больше нуля, получено: {amount}"
            )
        if self.stock < amount:
            raise InsufficientStockError(
                f"Товара недостаточно. На складе: {self.stock}, требуется: {amount}"
            )
        self.stock -= amount
        return self.stock


def process_order(product, amount):
    try:
        left = product.sell(amount)
        print(f"Продано {amount} шт. товара '{product.name}'. Остаток: {left}")
    except InsufficientStockError as e:
        print("Ошибка склада:", e)
    except SFMShopException as e:
        print("Ошибка проекта:", e)


product = Product("Ноутбук", 10)
process_order(product, 3)
process_order(product, 100)
process_order(product, -5)
process_order(product, 7)

# ==================
# УРОК: HTTP-ЗАПРОСЫ И ОТВЕТЫ
# ==================

# Практика: Задание 2 - Мини-роутер запросов SFMShop
from http import HTTPStatus

# Каталог товаров SFMShop (in-memory)
PRODUCTS = {
    1: {"id": 1, "name": "Ноутбук", "price": 50000},
    2: {"id": 2, "name": "Мышь", "price": 1500},
}


def handle_request(method, path):
    """Возвращает кортеж (числовой статус, текстовая причина, тело-строка)
    по HTTP-методу и пути. Реализует endpoint'ы SFMShop."""

    # GET /products - список товаров
    if method == "GET" and path == "/products":
        names = ", ".join(p["name"] for p in PRODUCTS.values())
        status = HTTPStatus.OK
        return (status.value, status.phrase, names)

    # GET /products/{id} - товар по ID
    if method == "GET" and path.startswith("/products/"):
        pid = int(path.split("/")[-1])
        if pid in PRODUCTS:
            status = HTTPStatus.OK
            return (status.value, status.phrase, PRODUCTS[pid]["name"])
        status = HTTPStatus.NOT_FOUND
        return (status.value, status.phrase, f"Товар с id={pid} не найден")

    # POST /orders - создание заказа
    if method == "POST" and path == "/orders":
        status = HTTPStatus.CREATED
        return (status.value, status.phrase, "Заказ создан")

    # DELETE /products/{id} - удаление товара
    if method == "DELETE" and path.startswith("/products/"):
        pid = int(path.split("/")[-1])
        if pid in PRODUCTS:
            status = HTTPStatus.OK
            return (status.value, status.phrase, "Товар удалён")
        status = HTTPStatus.NOT_FOUND
        return (status.value, status.phrase, f"Товар с id={pid} не найден")

    # Метод/путь не поддерживается endpoint'ом
    status = HTTPStatus.NOT_FOUND
    return (status.value, status.phrase, "Endpoint не найден")


requests = [
    ("GET", "/products"),
    ("GET", "/products/1"),
    ("GET", "/products/999"),
    ("POST", "/orders"),
    ("DELETE", "/products/2"),
]

for method, path in requests:
    code, phrase, body = handle_request(method, path)
    print(f"{method} {path} -> {code} {phrase} | {body}")

# ==================
# УРОК 31: ОБЗОРНО И БАЗОВО ПРО АЛГОРИТМЫ
# ==================

# Решение задачи от тимлида - быстрый поиск товара по ID
# Каталог SFMShop вырос до 10 000 товаров, и линейный поиск по списку (O(n))
# стал слишком медленным. Строим словарь-индекс по ID один раз и дальше
# ищем за константное время O(1).
class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price


def create_products_index(products):
    """Создать словарь для быстрого поиска"""
    return {product.id: product for product in products}


def find_product(products_index, product_id):
    """Быстрый поиск в словаре"""
    return products_index.get(product_id)


products = [
    Product(101, "Ноутбук", 50000),
    Product(103, "Клавиатура", 3000),
    Product(105, "Мышь", 1500),
    Product(108, "Наушники", 7000),
    Product(110, "Монитор", 18000),
]

# Индекс строится один раз, дальше каждый поиск - O(1)
products_index = create_products_index(products)

found = find_product(products_index, 108)
print("Найден товар:", found.name)

missing = find_product(products_index, 104)
print("Товар с ID 104:", missing)


# ==================
# УРОК 32: ГЛУБЖЕ О НАСЛЕДОВАНИИ, ПОЛИМОРФИЗМЕ, ИНКАПСУЛЯЦИИ, АБСТРАКЦИИ
# ==================

# Практика: Задание 2 - Скидки корзины через абстрактный класс и композицию
from abc import ABC, abstractmethod


class Discount(ABC):
    """Абстрактный класс скидки"""

    @abstractmethod
    def apply(self, total: float) -> float:
        """Вернуть итоговую сумму после применения скидки"""
        pass

    @abstractmethod
    def describe(self) -> str:
        """Короткое описание скидки"""
        pass


class PercentDiscount(Discount):
    """Процентная скидка"""

    def __init__(self, percent: float):
        self.percent = percent

    def apply(self, total: float) -> float:
        return total * (1 - self.percent / 100)

    def describe(self) -> str:
        return f"-{self.percent:.0f}%"


class FixedDiscount(Discount):
    """Фиксированная скидка в рублях"""

    def __init__(self, amount: float):
        self.amount = amount

    def apply(self, total: float) -> float:
        return max(0.0, total - self.amount)

    def describe(self) -> str:
        return f"-{self.amount:.0f} руб."


class Cart:
    """Корзина SFMShop: ИМЕЕТ скидку (композиция)"""

    def __init__(self, discount: Discount):
        self.discount = discount
        self.items = []

    def add(self, name: str, price: float) -> None:
        self.items.append((name, price))

    def total(self) -> float:
        base = sum(price for _, price in self.items)
        return self.discount.apply(base)


def checkout(cart: Cart) -> None:
    """Полиморфизм: работает с любой скидкой"""
    print(f"Товаров в корзине: {len(cart.items)}")
    print(f"Скидка: {cart.discount.describe()}")
    print(f"К оплате: {cart.total():.2f} руб.")


# Использование
cart1 = Cart(PercentDiscount(20))
cart1.add("Футболка", 1500)
cart1.add("Кепка", 1000)
checkout(cart1)

cart2 = Cart(FixedDiscount(500))
cart2.add("Худи", 3000)
checkout(cart2)

# ==================
# УРОК 33 (ba7): ГЛУБЖЕ О МАГИЧЕСКИХ МЕТОДАХ
# ==================

# Практика: Задание 2 - Корзина SFMShop через магические методы
class Cart:
    def __init__(self):
        self.items = []  # список (название, цена)

    def __add__(self, item):
        new_cart = Cart()
        new_cart.items = self.items.copy()
        new_cart.items.append(item)
        return new_cart

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def __call__(self):
        return sum(price for _, price in self.items)


cart = Cart()
cart = cart + ("Ноутбук", 75000)
cart = cart + ("Мышь", 1200)
cart = cart + ("Клавиатура", 3500)

print(len(cart))
print(cart[0][0])
for name, price in cart:
    print(f"{name}: {price}")
print(cart())

# ==================
# УРОК 34 (ba7): @property, @classmethod, @staticmethod, @dataclass
# ==================

# Практика: Задание 2 - Альтернативный конструктор и расчёт скидки
class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    @classmethod
    def from_dict(cls, data):
        """Альтернативный конструктор из словаря"""
        return cls(data["name"], data["price"], data["quantity"])

    @staticmethod
    def calculate_discount(price, discount_percent):
        """Цена со скидкой в процентах"""
        return price * (1 - discount_percent / 100)


raw_products = [
    {"name": "Ноутбук", "price": 1000, "quantity": 10},
    {"name": "Мышь", "price": 500, "quantity": 20},
    {"name": "Клавиатура", "price": 800, "quantity": 5},
]

products = [Product.from_dict(item) for item in raw_products]

for product in products:
    sale_price = Product.calculate_discount(product.price, 25)
    print(f"{product.name}: {product.price} -> {sale_price}")


# ==================
# УРОК 36 (ba7): Миксины
# ==================

# Практика: Задание 2 - Комбинирование двух миксинов в классе Product
class DiscountableMixin:
    """Миксин для расчёта цены со скидкой"""

    def apply_discount(self, percent):
        if percent < 0 or percent > 100:
            raise ValueError("Процент скидки должен быть от 0 до 100")
        discounted = self.price * (1 - percent / 100)
        return round(discounted, 2)


class SerializableMixin:
    """Миксин для представления объекта в виде словаря"""

    def to_dict(self):
        return {"class": self.__class__.__name__, "data": self.__dict__}


class Product(DiscountableMixin, SerializableMixin):
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity


product = Product("Ноутбук", 1000, 5)

print(product.apply_discount(15))
print(product.apply_discount(0))
print(product.to_dict())

try:
    product.apply_discount(150)
except ValueError as e:
    print(f"Ошибка: {e}")

print([cls.__name__ for cls in Product.__mro__])


# ==================
# УРОК 37 (ba7): SOLID принципы
# ==================

# Практика: Задание 2 - Стратегии доставки через OCP
from abc import ABC, abstractmethod


class DeliveryStrategy(ABC):
    """Абстракция стоимости доставки (OCP)"""
    @abstractmethod
    def cost(self, order_sum: float) -> float:
        ...


class PickupDelivery(DeliveryStrategy):
    """Самовывоз — бесплатно"""
    def cost(self, order_sum: float) -> float:
        return 0.0


class CourierDelivery(DeliveryStrategy):
    """Курьер — 300 руб., но бесплатно от 5000 руб."""
    def cost(self, order_sum: float) -> float:
        return 0.0 if order_sum >= 5000 else 300.0


class PostDelivery(DeliveryStrategy):
    """Почта — фиксированные 450 руб."""
    def cost(self, order_sum: float) -> float:
        return 450.0


class Order:
    """Только хранение данных заказа (SRP)"""
    def __init__(self, order_id: int, order_sum: float):
        self.order_id = order_id
        self.order_sum = order_sum


def final_price(order: Order, delivery: DeliveryStrategy) -> float:
    """Открыт для расширения новыми стратегиями, закрыт для модификации (OCP)"""
    return order.order_sum + delivery.cost(order.order_sum)


orders = [
    (Order(1, 3000.0), CourierDelivery()),
    (Order(2, 6000.0), CourierDelivery()),
    (Order(3, 1500.0), PickupDelivery()),
    (Order(4, 2000.0), PostDelivery()),
]

for order, delivery in orders:
    strategy_name = type(delivery).__name__
    total = final_price(order, delivery)
    print(f"Заказ {order.order_id} ({strategy_name}): {total:.2f} руб.")


# ==================
# УРОК 38 (ba7): Метаклассы
# ==================

# Практика: Задание 2 - Автоматическая регистрация моделей в реестре
class ModelMeta(type):
    """Метакласс, который автоматически регистрирует классы моделей в реестре"""
    _registry = {}

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if name != "Model":
            cls._registry[name] = new_class
        return new_class


class Model(metaclass=ModelMeta):
    pass


class Product(Model):
    def __init__(self, name, price):
        self.name = name
        self.price = price


class Order(Model):
    def __init__(self, order_id, total):
        self.order_id = order_id
        self.total = total


class User(Model):
    def __init__(self, login):
        self.login = login


for model_name in sorted(ModelMeta._registry):
    print(model_name)

print("Всего моделей:", len(ModelMeta._registry))
print("Order зарегистрирован:", "Order" in ModelMeta._registry)
print("Model в реестре:", "Model" in ModelMeta._registry)


# ==================
# УРОК 39 (ba7): Дескрипторы
# ==================

# Практика: Задание 2 - Дескриптор OneOf для статуса заказа
class OneOf:
    """Дескриптор: разрешает только значения из заданного набора"""

    def __init__(self, *allowed):
        self.allowed = set(allowed)

    def __set_name__(self, owner, name):
        # Python сам передаёт сюда имя поля при объявлении класса
        self.storage_name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        if value not in self.allowed:
            allowed_str = ", ".join(sorted(self.allowed))
            raise ValueError(f"Недопустимое значение: {value}. Разрешено: {allowed_str}")
        setattr(instance, self.storage_name, value)


class Order:
    status = OneOf("new", "paid", "shipped", "cancelled")

    def __init__(self, order_id, status):
        self.order_id = order_id
        self.status = status


order = Order(1, "new")
print(order.status)

order.status = "paid"
print(order.status)

try:
    order.status = "deleted"
except ValueError as e:
    print(f"Ошибка: {e}")


# ==================
# УРОК 40 (ba7): РЕФАКТОРИНГ КОДА
# ==================

# Практика: Задание 2 - Рефакторинг расчёта доставки по OCP
# Жёсткий if/elif по типу доставки вынесен в стратегии за общим
# интерфейсом ShippingStrategy. ShippingCalculator не знает о конкретных
# тарифах - он лишь вызывает strategy.cost(weight), поэтому добавить новый
# способ доставки можно без его правки (принцип OCP).
from abc import ABC, abstractmethod


class ShippingStrategy(ABC):
    @abstractmethod
    def cost(self, weight: float) -> float:
        pass


class CourierShipping(ShippingStrategy):
    def cost(self, weight: float) -> float:
        return 300 + 50 * weight


class PickupShipping(ShippingStrategy):
    def cost(self, weight: float) -> float:
        return 0.0


class PostShipping(ShippingStrategy):
    def cost(self, weight: float) -> float:
        return 200 + 20 * weight


class ShippingCalculator:
    @staticmethod
    def calculate(weight: float, strategy: ShippingStrategy) -> float:
        return strategy.cost(weight)


shipping_orders = [
    ("Заказ №1", 4.0, CourierShipping()),
    ("Заказ №2", 4.0, PickupShipping()),
    ("Заказ №3", 4.0, PostShipping()),
]

for name, weight, strategy in shipping_orders:
    cost = ShippingCalculator.calculate(weight, strategy)
    print(f"{name}: {cost:.2f} руб.")


# ==================
# ДЕМОНСТРАЦИЯ ПРОДВИНУТЫХ КОНЦЕПЦИЙ ООП
# ==================

from models.order_factory import OrderFactory
from models.delivery_stragedy import StandardDelivery
from models.payment import CardPayment
from models.product import Product
from models.user import User


def process_advanced_order_system():
    """Демонстрация всех продвинутых концепций ООП"""

    user = User("Иван Иванов", "ivan@test.ru")
    items = [
        Product("Ноутбук", 1000, 10),
        Product("Мышь", 500, 5),
    ]

    # 1. Factory для создания заказов
    order = OrderFactory.create_order(1, items, user)

    # 2. Strategy для расчета доставки
    delivery = StandardDelivery()
    delivery_cost = delivery.calculate_cost(5.0)

    # 3. Полиморфизм для платежей
    payment = CardPayment(1000)
    payment.process()

    # 4. Метакласс для сериализации
    order_json = order.to_dict()

    # 5. Дескрипторы для валидации
    product = Product("Ноутбук", 1000, 10)  # Автоматическая валидация

    # 6. Миксины для логирования
    payment.log("Платеж обработан")

    # 7. Магические методы
    print(len(order))  # Количество товаров
    print("Ноутбук" in order)  # Проверка наличия

    return {
        "order": order_json,
        "delivery_cost": delivery_cost,
        "product": product.to_dict()
    }


print(process_advanced_order_system())

# ==================
# УРОК 41: Доступ к базе данных PostgreSQL
# ==================

# Практика: Задание 2 - Схема SFMShop и отчёт по выручке (sqlite3)
import sqlite3


def setup_database():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT)")
    conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, quantity INTEGER)")
    conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, product_id INTEGER, quantity INTEGER)")
    conn.commit()
    return conn


def seed(conn):
    conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("John Doe", "john@example.com"))
    conn.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", ("Product 1", 100, 10))
    conn.execute("INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)", (1, 1, 1))
    conn.commit()


def report(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT users.name, SUM(products.price * orders.quantity) AS total FROM users JOIN orders ON users.id = orders.user_id JOIN products ON orders.product_id = products.id GROUP BY users.name")
    orders = cursor.fetchall()
    for user, total in orders:
        print(f"{user}: {total:.2f} руб.")

if __name__ == "__main__":
    conn = setup_database()
    seed(conn)
    report(conn)
    conn.close()