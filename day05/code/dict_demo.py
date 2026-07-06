# -*- coding: utf-8 -*-
"""
星火科技 · 培训 Day 5
文件：dict_demo.py
说明：字典 CRUD、嵌套访问、遍历、与 JSON 互转的教学演示。

对应讲义章节：
    第一节 demo_crud()      —— 第二章 字典 CRUD
    第二节 demo_nested()    —— 第三章 嵌套字典
    第三节 demo_iteration() —— 第三章 遍历
    第四节 demo_json_preview() —— 第四章 JSON 预览

运行方式：
    python3 dict_demo.py           # 运行全部演示
    python3 dict_demo.py crud      # 仅运行某一节

作者：培训生（请修改）
日期：2026-07-10
"""

from __future__ import annotations

import json
import sys
from typing import Any


def demo_crud() -> None:
    """
    演示字典的增删改查（Create / Read / Update / Delete）。

    业务类比：维护单条员工记录的内存表示，尚未涉及文件或 API。
    """
    print("=" * 60)
    print("第一节 · 字典 CRUD")
    print("=" * 60)

    # --- Create：字面量创建 ---
    employee: dict[str, Any] = {
        "name": "陈晓",
        "employee_id": "ST-2026-001",
    }
    print("创建后:", employee)

    # --- Read：方括号 vs get ---
    print("姓名:", employee["name"])  # 键必须存在，否则 KeyError
    print("邮箱:", employee.get("email"))  # 不存在返回 None
    print("邮箱(默认):", employee.get("email", "未填写"))

    # --- Update：单键赋值与批量 update ---
    employee["department"] = "大模型应用开发部"
    employee.update({"phone": "13800138000", "need_dorm": True})
    print("更新后:", employee)

    # --- Delete：del 与 pop ---
    removed = employee.pop("need_dorm", None)  # 安全删除，返回被删的值
    print("删除 need_dorm，返回值:", removed)
    print("删除后:", employee)

    # --- 成员检测 ---
    print("'name' in employee:", "name" in employee)
    print("'salary' not in employee:", "salary" not in employee)


def demo_nested() -> None:
    """
    演示嵌套 dict / list 的安全访问。

    结构对齐 mock_api_response.json 的简化版，便于理解 parse_api 在做什么。
    """
    print("\n" + "=" * 60)
    print("第二节 · 嵌套字典")
    print("=" * 60)

    # 模拟 API 根对象（内存中的 dict，不是 JSON 字符串）
    api_root: dict[str, Any] = {
        "code": 200,
        "message": "success",
        "data": {
            "employees": [
                {"name": "陈晓", "employee_id": "ST-2026-001"},
                {"name": "李雷", "employee_id": "ST-2026-003"},
            ],
            "pagination": {"page": 1, "total": 2},
        },
    }

    # 不推荐：链式方括号，中间任一层缺失都会 KeyError
    # employees = api_root["data"]["employees"]

    # 推荐：分层 .get()，缺失时落到空 dict / 空 list
    data = api_root.get("data") or {}
    employees = data.get("employees") or []
    pagination = data.get("pagination") or {}

    print("业务码:", api_root.get("code"))
    print("员工条数:", len(employees))
    print("第一名员工:", employees[0] if employees else "无数据")
    print("分页 total:", pagination.get("total"))

    # 访问列表中第二个员工的工号
    if len(employees) >= 2:
        second_id = employees[1].get("employee_id", "未知")
        print("第二名工号:", second_id)


def demo_iteration() -> None:
    """
    演示 keys / values / items 及遍历 list[dict]。

    日后 RAG 检索结果 documents[]、API messages[] 都用同样写法。
    """
    print("\n" + "=" * 60)
    print("第三节 · 字典遍历")
    print("=" * 60)

    employees: list[dict[str, Any]] = [
        {"name": "陈晓", "employee_id": "ST-2026-001", "need_dorm": True},
        {"name": "李雷", "employee_id": "ST-2026-003", "need_dorm": False},
    ]

    # 遍历单条 dict 的键值对
    sample = employees[0]
    print("--- items() 遍历单条记录 ---")
    for key, value in sample.items():
        print(f"  {key}: {value!r}")

    print("--- 遍历员工列表 ---")
    for index, emp in enumerate(employees, start=1):
        dorm = "住宿" if emp.get("need_dorm") else "不住宿"
        print(f"  [{index}] {emp.get('name')} / {emp.get('employee_id')} / {dorm}")

    # 仅收集工号列表（列表推导式预习 Day 4）
    ids = [e.get("employee_id", "") for e in employees]
    print("工号列表:", ids)


def demo_json_preview() -> None:
    """
    演示 dict 与 JSON 字符串互转（loads / dumps）。

    注意 Python True/None 与 JSON true/null 的书写差异。
    """
    print("\n" + "=" * 60)
    print("第四节 · JSON 互转预览")
    print("=" * 60)

    # Python dict：布尔是 True，空值是 None
    employee_py: dict[str, Any] = {
        "name": "陈晓",
        "need_dorm": True,
        "extra": None,
    }

    # dumps：Python 对象 → JSON 格式字符串
    json_text = json.dumps(employee_py, ensure_ascii=False, indent=2)
    print("--- dumps 输出（注意 true 和 null）---")
    print(json_text)

    # loads：JSON 字符串 → Python 对象
    restored = json.loads(json_text)
    print("--- loads 后类型 ---")
    print("need_dorm 类型:", type(restored["need_dorm"]))
    print("extra 值:", restored["extra"], "类型:", type(restored["extra"]))


# 演示节名称到函数的映射，支持命令行选择性运行
DEMO_MAP: dict[str, callable] = {
    "crud": demo_crud,
    "nested": demo_nested,
    "iteration": demo_iteration,
    "json": demo_json_preview,
}


def main() -> None:
    """根据命令行参数运行全部或单节演示。"""
    if len(sys.argv) > 1:
        name = sys.argv[1].lower()
        func = DEMO_MAP.get(name)
        if func is None:
            print(f"未知演示节: {name}，可选: {', '.join(DEMO_MAP)}")
            sys.exit(1)
        func()
        return

    demo_crud()
    demo_nested()
    demo_iteration()
    demo_json_preview()


if __name__ == "__main__":
    main()
