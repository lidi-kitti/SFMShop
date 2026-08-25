-- Таблица пользователей
CREATE TABLE users (
 id SERIAL PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 email VARCHAR(100) UNIQUE NOT NULL,
 balance DECIMAL(12,2) NOT NULL DEFAULT 0 CHECK (balance >= 0)
);
-- Таблица продуктов
CREATE TABLE products (
id SERIAL PRIMARY KEY, 
name VARCHAR(200) NOT NULL, 
price DECIMAL(10,2) NOT NULL CHECK (price >= 0), 
quantity INTEGER DEFAULT 5 CHECK (quantity >= 0));
-- Таблица заказов
CREATE TABLE orders (
 id SERIAL PRIMARY KEY,
 user_id INTEGER NOT NULL REFERENCES users(id),
 total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
 created_at TIMESTAMP DEFAULT NOW()
);
-- Таблица заказы на товары
CREATE TABLE order_items (
 id SERIAL PRIMARY KEY,
 order_id INTEGER NOT NULL REFERENCES orders(id), 
 product_id INTEGER NOT NULL REFERENCES products(id), 
 quantity INTEGER NOT NULL CHECK (quantity > 0),
 price DECIMAL(10,2) NOT NULL CHECK (price >= 0)
);

-- Тестовые данные
INSERT INTO users (name, email, balance) VALUES
 ('Иван', 'ivan@test.com', 100000.00),
 ('Мария', 'maria@test.com', 50000.00),
 ('Петр', 'petr@test.com', 25000.00);

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
