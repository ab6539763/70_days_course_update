# -*- coding: utf-8 -*-
"""Day 4 主程序：命令行待办管理器（内存版）。

运行：python3 todo_manager.py

功能：add / list / complete / delete（PRD-SPARK-TODO-004）
数据：todos 为 list[dict]，进程退出后数据不保留（Day 5 学 JSON 持久化）

与 Day 48 衔接：Planner Agent 的 task_list 工具将复用今日 CRUD 思路。
"""

from __future__ import annotations

# 优先级排序权重（tuple 定义合法值，dict 定义排序顺序）
VALID_PRIORITIES: tuple[str, ...] = ("P0", "P1", "P2")
PRIORITY_RANK: dict[str, int] = {"P0": 0, "P1": 1, "P2": 2}


def find_index_by_id(todos: list[dict], todo_id: int) -> int | None:
    """按 id 线性查找，返回在 todos 中的索引；找不到返回 None。"""
    for i, item in enumerate(todos):
        if item["id"] == todo_id:
            return i
    return None


def parse_tags(raw: str) -> list[str]:
    """逗号分隔标签 → strip → set 去重 → 排序后转回 list。"""
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return sorted(set(parts))


def add_todo(
    todos: list[dict],
    next_id: int,
    title: str,
    priority: str = "P1",
    tags: list[str] | None = None,
) -> int:
    """添加一条待办，append 到 todos 尾部，返回更新后的 next_id。"""
    title = title.strip()
    if not title:
        raise ValueError("标题不能为空，请重新输入。")
    if priority not in VALID_PRIORITIES:
        priority = "P1"
    item = {
        "id": next_id,
        "title": title,
        "done": False,
        "priority": priority,
        "tags": tags or [],
    }
    todos.append(item)
    return next_id + 1


def format_todo(item: dict) -> str:
    """格式化单条待办，供终端展示。"""
    mark = "[x]" if item["done"] else "[ ]"
    tag_str = ",".join(item["tags"]) if item["tags"] else "-"
    return f"[#{item['id']}] {mark} {item['priority']} | {item['title']} | tags: {tag_str}"


def list_todos(
    todos: list[dict],
    filter_mode: str = "1",
    sort_by_priority: bool = False,
) -> list[dict]:
    """过滤并可选排序，返回要展示的子列表（不修改原 todos）。"""
    if filter_mode == "2":
        filtered = [t for t in todos if not t["done"]]
    elif filter_mode == "3":
        filtered = [t for t in todos if t["done"]]
    else:
        filtered = list(todos)

    if sort_by_priority:
        return sorted(filtered, key=lambda t: (PRIORITY_RANK.get(t["priority"], 1), t["id"]))
    return sorted(filtered, key=lambda t: t["id"])


def complete_todo(todos: list[dict], todo_id: int) -> bool:
    """将指定 id 标记为已完成。成功返回 True，id 不存在返回 False。"""
    idx = find_index_by_id(todos, todo_id)
    if idx is None:
        return False
    if todos[idx]["done"]:
        print(f"提示：#{todo_id} 已经是完成状态。")
        return True
    todos[idx]["done"] = True
    return True


def delete_todo(todos: list[dict], todo_id: int) -> bool:
    """按 id 删除待办。成功返回 True，id 不存在返回 False。"""
    idx = find_index_by_id(todos, todo_id)
    if idx is None:
        return False
    removed = todos.pop(idx)
    print(f"已删除 #{removed['id']}: {removed['title']}")
    return True


def print_stats(todos: list[dict]) -> None:
    """统计总数、完成数、完成率（作业 B4 课堂版已实现）。"""
    total = len(todos)
    done = sum(1 for t in todos if t["done"])
    rate = (done / total * 100) if total else 0.0
    print(f"\n统计：总计 {total}，已完成 {done}，完成率 {rate:.1f}%")


def print_banner() -> None:
    print("\n" + "=" * 48)
    print("  星火科技 · 内部待办管理器 v1.0")
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
    """交互：收集标题、优先级、标签并调用 add_todo。"""
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
    """交互：选择过滤条件与排序方式后打印。"""
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
    todo_id = int(raw)
    if complete_todo(todos, todo_id):
        if find_index_by_id(todos, todo_id) is not None:
            print(f"已将 #{todo_id} 标记为完成。")
    else:
        print(f"错误：找不到 id=#{todo_id} 的待办。")


def handle_delete(todos: list[dict]) -> None:
    raw = input("要删除的项目 id: ").strip()
    if not raw.isdigit():
        print("请输入有效数字 id。")
        return
    todo_id = int(raw)
    if not delete_todo(todos, todo_id):
        print(f"错误：找不到 id=#{todo_id} 的待办。")


def main() -> None:
    """主循环：Day 3 while + Day 4 list 状态管理。"""
    todos: list[dict] = []
    next_id = 1

    print_banner()
    print("李姐：「下周 Sprint 规划前，先把任务录进来。」")
    print("张工：「list 练熟后，Day 48 Agent 任务列表就是同一套 CRUD。」")

    while True:
        print_menu()
        choice = input("\n请选择: ").strip().lower()

        if choice in ("0", "quit", "q", "exit"):
            print("\n已退出。提示：数据未持久化，Day 5 将学习 JSON 保存到文件。")
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
            print_stats(todos)
        else:
            print("无效选项，请输入 0-5 或命令名。")


if __name__ == "__main__":
    main()
