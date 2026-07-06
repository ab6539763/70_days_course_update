# -*- coding: utf-8 -*-
"""
Day 47 · 销售库种子数据

运行：cd day47/code && python3 seed_sales_data.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
DB_PATH = CODE_DIR / "data" / "sales.db"
SCHEMA_PATH = CODE_DIR / "sales_schema.sql"

CUSTOMERS = [
    ("杭州星云科技", "杭州", "Enterprise"),
    ("上海澄明贸易", "上海", "SMB"),
    ("北京智行教育", "北京", "Consumer"),
    ("深圳蓝海制造", "深圳", "Enterprise"),
    ("成都味来餐饮", "成都", "SMB"),
]

PRODUCTS = [
    ("ST-API-01", "星火 API 套餐", "SaaS", 2999.0),
    ("ST-RAG-02", "企业知识库模块", "SaaS", 8999.0),
    ("ST-BOT-03", "智能客服 Bot", "SaaS", 4999.0),
    ("ST-TRAIN-04", "培训服务人天", "Service", 1800.0),
    ("ST-HW-05", "推理网关硬件", "Hardware", 12800.0),
]

ORDERS = [
    (1, "2026-05-10", "shipped", "华东"),
    (1, "2026-06-01", "paid", "华东"),
    (2, "2026-05-15", "shipped", "华东"),
    (3, "2026-05-20", "paid", "华北"),
    (4, "2026-06-05", "shipped", "华南"),
    (5, "2026-06-12", "pending", "西南"),
]

ORDER_ITEMS = [
    (1, 1, 2, 5998.0),
    (1, 2, 1, 8999.0),
    (2, 3, 1, 4999.0),
    (3, 4, 3, 5400.0),
    (4, 5, 1, 12800.0),
    (5, 1, 1, 2999.0),
]


def init_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    return conn


def seed(conn: sqlite3.Connection) -> dict[str, int]:
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO customers (name, city, segment) VALUES (?, ?, ?)",
        CUSTOMERS,
    )
    cur.executemany(
        "INSERT INTO products (sku, name, category, unit_price) VALUES (?, ?, ?, ?)",
        PRODUCTS,
    )
    cur.executemany(
        "INSERT INTO orders (customer_id, order_date, status, region) VALUES (?, ?, ?, ?)",
        ORDERS,
    )
    cur.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, line_amount) VALUES (?, ?, ?, ?)",
        ORDER_ITEMS,
    )
    conn.commit()
    counts = {
        "customers": cur.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
        "products": cur.execute("SELECT COUNT(*) FROM products").fetchone()[0],
        "orders": cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "order_items": cur.execute("SELECT COUNT(*) FROM order_items").fetchone()[0],
    }
    return counts


def main() -> None:
    conn = init_db()
    counts = seed(conn)
    conn.close()
    print(f"Seeded {DB_PATH}")
    for table, n in counts.items():
        print(f"  {table}: {n}")


if __name__ == "__main__":
    main()
