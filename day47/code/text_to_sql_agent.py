# -*- coding: utf-8 -*-
"""
Day 47 · Text-to-SQL Agent（SQLite 销售库 · mock 模式）

流程：
1. 将 schema + 用户问题发给 mock LLM
2. 解析 SELECT 语句
3. 安全校验（仅允许 SELECT）
4. 执行并自然语言总结

运行：
  cd day47/code
  python3 seed_sales_data.py
  python3 text_to_sql_agent.py
"""

from __future__ import annotations

import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CODE_DIR = Path(__file__).resolve().parent
DB_PATH = CODE_DIR / "data" / "sales.db"
SCHEMA_PATH = CODE_DIR / "sales_schema.sql"

FORBIDDEN_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|PRAGMA|REPLACE|TRUNCATE)\b",
    re.I,
)

SCHEMA_SUMMARY = """
表 customers(customer_id, name, city, segment, created_at)
表 products(product_id, sku, name, category, unit_price)
表 orders(order_id, customer_id, order_date, status, region)
表 order_items(item_id, order_id, product_id, quantity, line_amount)
关联：orders.customer_id -> customers.customer_id
      order_items.order_id -> orders.order_id
      order_items.product_id -> products.product_id
""".strip()


@dataclass
class SQLResult:
    sql: str
    rows: list[dict[str, Any]]
    summary: str
    mock: bool = True


class MockTextToSQL:
    """启发式 mock：常见分析问题 → SELECT。"""

    def generate_sql(self, question: str) -> str:
        q = question.lower()
        if "总额" in question or "销售额" in question or "收入" in question:
            return "SELECT SUM(line_amount) AS total_sales FROM order_items;"
        if "品类" in question or "category" in q:
            return (
                "SELECT p.category, SUM(oi.line_amount) AS revenue "
                "FROM order_items oi JOIN products p ON oi.product_id = p.product_id "
                "GROUP BY p.category ORDER BY revenue DESC;"
            )
        if "城市" in question or "city" in q:
            return (
                "SELECT c.city, COUNT(o.order_id) AS order_count "
                "FROM customers c JOIN orders o ON c.customer_id = o.customer_id "
                "GROUP BY c.city ORDER BY order_count DESC;"
            )
        if "enterprise" in q or "企业客户" in question:
            return (
                "SELECT c.name, SUM(oi.line_amount) AS total "
                "FROM customers c "
                "JOIN orders o ON c.customer_id = o.customer_id "
                "JOIN order_items oi ON o.order_id = oi.order_id "
                "WHERE c.segment = 'Enterprise' "
                "GROUP BY c.name ORDER BY total DESC;"
            )
        if "订单" in question and "数" in question:
            return "SELECT COUNT(*) AS order_count FROM orders;"
        if "pending" in q or "待处理" in question:
            return "SELECT order_id, order_date, region FROM orders WHERE status = 'pending';"
        return (
            "SELECT p.name, SUM(oi.quantity) AS qty "
            "FROM order_items oi JOIN products p ON oi.product_id = p.product_id "
            "GROUP BY p.name ORDER BY qty DESC LIMIT 5;"
        )


def validate_sql(sql: str) -> str:
    cleaned = sql.strip().rstrip(";")
    if not cleaned.upper().startswith("SELECT"):
        raise ValueError("仅允许 SELECT 查询")
    if FORBIDDEN_SQL.search(cleaned):
        raise ValueError("检测到危险 SQL 关键字")
    if ";" in cleaned:
        raise ValueError("不允许多语句")
    return cleaned + ";"


def execute_sql(db_path: Path, sql: str) -> list[dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(sql)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def summarize(question: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "查询无结果。"
    if len(rows) == 1 and len(rows[0]) == 1:
        key, val = next(iter(rows[0].items()))
        return f"根据销售库，{question} 的答案是 {key}={val}。"
    preview = rows[:3]
    return f"共 {len(rows)} 行。示例：{preview}"


class TextToSQLAgent:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.llm = MockTextToSQL()

    def ask(self, question: str) -> SQLResult:
        if not self.db_path.is_file():
            raise FileNotFoundError(f"数据库不存在，请先运行 seed_sales_data.py: {self.db_path}")
        raw_sql = self.llm.generate_sql(question)
        safe_sql = validate_sql(raw_sql)
        rows = execute_sql(self.db_path, safe_sql)
        summary = summarize(question, rows)
        return SQLResult(sql=safe_sql, rows=rows, summary=summary)

    def schema_hint(self) -> str:
        return SCHEMA_SUMMARY


def repl() -> None:
    agent = TextToSQLAgent()
    print("=== Day 47 Text-to-SQL Agent (mock) ===")
    print("示例：总销售额多少？各品类收入？各城市订单数？")
    print("命令：/schema /exit")
    while True:
        try:
            q = input("\n问> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break
        if not q:
            continue
        if q == "/exit":
            break
        if q == "/schema":
            print(agent.schema_hint())
            continue
        try:
            r = agent.ask(q)
            print(f"SQL> {r.sql}")
            print(f"答> {r.summary}")
        except Exception as exc:  # noqa: BLE001
            print(f"[error] {exc}")


def main() -> None:
    os.environ.setdefault("SPARKTECH_MOCK", "1")
    if not DB_PATH.is_file():
        from seed_sales_data import main as seed_main

        seed_main()
    repl()


if __name__ == "__main__":
    main()
