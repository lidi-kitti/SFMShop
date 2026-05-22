-- Таблица пользователей
CREATE TABLE users (
 id SERIAL PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 email VARCHAR(100) UNIQUE NOT NULL
);
-- Таблица продуктов
CREATE TABLE products (
id SERIAL PRIMARY KEY, 
name VARCHAR(200) NOT NULL, 
price DECIMAL(10,2) NOT NULL, 
quantity INTEGER DEFAULT 5);
-- Таблица заказов
CREATE TABLE orders (
 id SERIAL PRIMARY KEY,
 user_id INTEGER REFERENCES users(id),
 total DECIMAL(10, 2) NOT NULL,
 created_at TIMESTAMP DEFAULT NOW()
);
-- Таблица заказы на товары
CREATE TABLE order_items (
 id SERIAL PRIMARY KEY,
 order_id INTEGER REFERENCES orders(id), 
 product_id INTEGER REFERENCES products(id), 
 quantity INTEGER
);

-- Тестовые данные
INSERT INTO users (name, email) VALUES
 ('Иван', 'ivan@test.com'),
 ('Мария', 'maria@test.com'),
 ('Петр', 'petr@test.com');

INSERT INTO products (name, price, quantity) VALUES
 ('Ноутбук', 50000.00, 10),
 ('Мышь', 1500.00, 20),
 ('Клавиатура', 3000.00, 15),
 ('Монитор', 20000.00, 5),
 ('Наушники', 5000.00, 12);

INSERT INTO orders (user_id, total) VALUES
 (1, 50000.00),
 (2, 3500.00);

INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
 (1, 1, 1, 50000.00),
 (2, 2, 1, 1500.00),
 (2, 3, 1, 3000.00);