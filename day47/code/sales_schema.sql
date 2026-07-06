-- Day 47 · 星火智服销售分析 SQLite  schema
-- 运行：sqlite3 data/sales.db < sales_schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    city          TEXT NOT NULL,
    segment       TEXT NOT NULL CHECK (segment IN ('SMB', 'Enterprise', 'Consumer')),
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE products (
    product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    sku           TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    category      TEXT NOT NULL,
    unit_price    REAL NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE orders (
    order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date    TEXT NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
    region        TEXT NOT NULL
);

CREATE TABLE order_items (
    item_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    line_amount   REAL NOT NULL CHECK (line_amount >= 0)
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_products_category ON products(category);
