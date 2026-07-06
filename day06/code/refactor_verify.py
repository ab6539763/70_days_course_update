# -*- coding: utf-8 -*-
"""
Day 6 自动化验收脚本：验证四个包的核心函数可导入且行为正确。
运行：cd day06/code && python3 refactor_verify.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))


def check_onboard() -> None:
    from sparktech_onboard import EmployeeCard, format_bool_display, render_card

    card = EmployeeCard(
        name="陈晓",
        employee_id="ST-2026-001",
        department="大模型应用开发部",
        onboard_date="2026-07-05",
        phone="13800138000",
        need_dorm=True,
    )
    text = render_card(card)
    assert "陈晓" in text
    assert format_bool_display(True) == "是"
    print("[OK] sparktech_onboard")


def check_cleaners() -> None:
    from sparktech_cleaners import CaseMode, normalize_case, remove_all_spaces, strip_edges

    assert strip_edges("  hello  ") == "hello"
    assert normalize_case("st-001", CaseMode.UPPER) == "ST-001"
    assert remove_all_spaces("138 0013 8001") == "13800138001"
    print("[OK] sparktech_cleaners")


def check_todo() -> None:
    from sparktech_todo import add_todo, complete_todo, list_todos

    todos: list[dict] = []
    nid = add_todo(todos, 1, "写讲义", "P0", ["day6"])
    assert nid == 2 and len(todos) == 1
    complete_todo(todos, 1)
    assert list_todos(todos, filter_mode="3")[0]["done"] is True
    print("[OK] sparktech_todo")


def check_export() -> None:
    from sparktech_export import export_employees_from_mock

    raw, cleaned, path = export_employees_from_mock()
    assert len(raw) == 5
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["name"] == "陈晓"
    assert data[1]["employee_id"] == "ST-2026-003"
    print("[OK] sparktech_export ->", path)


def main() -> None:
    print("Day 6 包重构验收")
    print("-" * 40)
    check_onboard()
    check_cleaners()
    check_todo()
    check_export()
    print("-" * 40)
    print("全部通过 ✓")


if __name__ == "__main__":
    main()
