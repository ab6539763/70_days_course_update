# -*- coding: utf-8 -*-
"""Day 47 验收脚本 —— 无 API Key 时全部 mock 通过。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ.setdefault("SPARKTECH_MOCK", "1")

from seed_sales_data import DB_PATH, init_db, seed  # noqa: E402
from text_to_sql_agent import (  # noqa: E402
    MockTextToSQL,
    TextToSQLAgent,
    validate_sql,
)


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def setup_db() -> None:
    conn = init_db()
    counts = seed(conn)
    conn.close()
    if counts["customers"] < 3:
        fail("种子数据 customers 过少")


def test_schema_files() -> None:
    schema = CODE_DIR / "sales_schema.sql"
    if not schema.is_file():
        fail("sales_schema.sql 缺失")
    text = schema.read_text(encoding="utf-8")
    for table in ("customers", "products", "orders", "order_items"):
        if table not in text:
            fail(f"schema 缺少表 {table}")
    ok("sales_schema.sql")


def test_seed() -> None:
    setup_db()
    if not DB_PATH.is_file():
        fail("sales.db 未生成")
    ok("seed_sales_data")


def test_sql_guard() -> None:
    try:
        validate_sql("SELECT 1;")
    except ValueError:
        fail("合法 SELECT 应通过")
    for bad in ("DROP TABLE customers;", "SELECT 1; DELETE FROM orders;", "INSERT INTO x VALUES(1)"):
        try:
            validate_sql(bad)
            fail(f"应拒绝危险 SQL: {bad}")
        except ValueError:
            pass
    ok("SQL validate SELECT-only")


def test_mock_sql_gen() -> None:
    llm = MockTextToSQL()
    sql = llm.generate_sql("总销售额是多少")
    assert sql.upper().startswith("SELECT")
    ok("MockTextToSQL")


def test_agent_queries() -> None:
    setup_db()
    agent = TextToSQLAgent()
    r1 = agent.ask("总销售额是多少")
    assert r1.rows
    total = list(r1.rows[0].values())[0]
    assert float(total) > 0

    r2 = agent.ask("各品类收入")
    assert len(r2.rows) >= 1

    r3 = agent.ask("各城市订单数")
    assert any("city" in row or "order_count" in row for row in r3.rows)

    r4 = agent.ask("Enterprise 客户销售额")
    assert r4.summary
    ok("TextToSQLAgent sales/city/segment")


def main() -> None:
    print("=== Day 47 verify ===\n")
    test_schema_files()
    test_seed()
    test_sql_guard()
    test_mock_sql_gen()
    test_agent_queries()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
