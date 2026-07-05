# -*- coding: utf-8 -*-
"""
星火科技 · Day 6 重构包 sparktech_todo
模块：cli.py
说明：待办管理器交互入口（自 Day 4 main 循环拆分）。
"""

from __future__ import annotations

from .core import (
    add_todo,
    complete_todo,
    compute_stats,
    delete_todo,
    format_todo,
    list_todos,
    parse_tags,
)


def print_banner() -> None:
    print("\n" + "=" * 48)
    print("  星火科技 · 内部待办管理器 v1.1（Day 6 包版）")
    print("  Sprint 规划前任务跟踪 | 数据仅存内存")
    print("=" * 48)


def print_menu() -> None:
    print("\n1. add      添加待办")
    print("2. list     查看列表")
    print("3. complete 标记完成")
    print("4. delete   删除待办")
    print("5. stats    查看统计")
    print("0. quit     退出")


def handle_add(todos: list[dict], next_id: int) -> int:
    title = input("任务标题: ").strip()
    try:
        priority = input("优先级 P0/P1/P2 [P1]: ").strip().upper() or "P1"
        tags_raw = input("标签（逗号分隔，可留空）: ").strip()
        tags = parse_tags(tags_raw) if tags_raw else []
        next_id = add_todo(todos, next_id, title, priority, tags)
        print(f"已添加 #{next_id - 1}: {title}")
    except ValueError as e:
        print(f"添加失败: {e}")
    return next_id


def handle_list(todos: list[dict]) -> None:
    if not todos:
        print("（暂无待办，使用 add 添加）")
        return
    print("列表过滤：1=全部  2=未完成  3=已完成")
    mode = input("选择 [1]: ").strip() or "1"
    sort_pri = input("按优先级排序？(y/n) [n]: ").strip().lower() in ("y", "yes", "是")
    items = list_todos(todos, filter_mode=mode, sort_by_priority=sort_pri)
    if not items:
        print("（当前过滤条件下无任务）")
        return
    print("-" * 48)
    for item in items:
        print(format_todo(item))
    print("-" * 48)


def handle_complete(todos: list[dict]) -> None:
    raw = input("要完成的项目 id: ").strip()
    if not raw.isdigit():
        print("请输入有效数字 id。")
        return
    ok, msg = complete_todo(todos, int(raw))
    print(msg if ok or "找不到" in msg else msg)


def handle_delete(todos: list[dict]) -> None:
    raw = input("要删除的项目 id: ").strip()
    if not raw.isdigit():
        print("请输入有效数字 id。")
        return
    ok, msg = delete_todo(todos, int(raw))
    print(msg)


def handle_stats(todos: list[dict]) -> None:
    s = compute_stats(todos)
    print(f"\n统计：总计 {s['total']}，已完成 {s['done']}，完成率 {s['rate']:.1f}%")


def run_cli() -> None:
    """主循环入口。"""
    todos: list[dict] = []
    next_id = 1
    print_banner()
    print("李姐：「下周 Sprint 规划前，先把任务录进来。」")
    print("张工：「Day 6 起逻辑在 sparktech_todo 包里，Day 14 直接 import。」")

    while True:
        print_menu()
        choice = input("\n请选择: ").strip().lower()
        if choice in ("0", "quit", "q", "exit"):
            print("\n已退出。提示：数据未持久化，Day 7 将学习文件读写。")
            break
        if choice in ("1", "add"):
            next_id = handle_add(todos, next_id)
        elif choice in ("2", "list"):
            handle_list(todos)
        elif choice in ("3", "complete"):
            handle_complete(todos)
        elif choice in ("4", "delete"):
            handle_delete(todos)
        elif choice in ("5", "stats"):
            handle_stats(todos)
        else:
            print("无效选项，请输入 0-5 或命令名。")
