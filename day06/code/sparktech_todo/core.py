# -*- coding: utf-8 -*-
"""
星火科技 · Day 6 重构包 sparktech_todo
模块：core.py
说明：待办 CRUD 纯函数（自 Day 4 todo_manager.py 拆分，无 print 副作用）。
"""

from __future__ import annotations

VALID_PRIORITIES: tuple[str, ...] = ("P0", "P1", "P2")
PRIORITY_RANK: dict[str, int] = {"P0": 0, "P1": 1, "P2": 2}


def find_index_by_id(todos: list[dict], todo_id: int) -> int | None:
    """按 id 线性查找索引。"""
    for i, item in enumerate(todos):
        if item["id"] == todo_id:
            return i
    return None


def parse_tags(raw: str) -> list[str]:
    """逗号分隔标签 → 去重排序。"""
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return sorted(set(parts))


def add_todo(
    todos: list[dict],
    next_id: int,
    title: str,
    priority: str = "P1",
    tags: list[str] | None = None,
) -> int:
    """添加待办，返回更新后的 next_id。"""
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
    """格式化单条待办。"""
    mark = "[x]" if item["done"] else "[ ]"
    tag_str = ",".join(item["tags"]) if item["tags"] else "-"
    return f"[#{item['id']}] {mark} {item['priority']} | {item['title']} | tags: {tag_str}"


def list_todos(
    todos: list[dict],
    filter_mode: str = "1",
    sort_by_priority: bool = False,
) -> list[dict]:
    """过滤并可选排序，返回子列表副本。"""
    if filter_mode == "2":
        filtered = [t for t in todos if not t["done"]]
    elif filter_mode == "3":
        filtered = [t for t in todos if t["done"]]
    else:
        filtered = list(todos)

    if sort_by_priority:
        return sorted(filtered, key=lambda t: (PRIORITY_RANK.get(t["priority"], 1), t["id"]))
    return sorted(filtered, key=lambda t: t["id"])


def complete_todo(todos: list[dict], todo_id: int) -> tuple[bool, str]:
    """
    标记完成。返回 (成功与否, 提示消息)。
    纯函数风格：不 print，由 CLI 层决定如何展示。
    """
    idx = find_index_by_id(todos, todo_id)
    if idx is None:
        return False, f"错误：找不到 id=#{todo_id} 的待办。"
    if todos[idx]["done"]:
        return True, f"提示：#{todo_id} 已经是完成状态。"
    todos[idx]["done"] = True
    return True, f"已将 #{todo_id} 标记为完成。"


def delete_todo(todos: list[dict], todo_id: int) -> tuple[bool, str]:
    """删除待办。返回 (成功与否, 提示消息)。"""
    idx = find_index_by_id(todos, todo_id)
    if idx is None:
        return False, f"错误：找不到 id=#{todo_id} 的待办。"
    removed = todos.pop(idx)
    return True, f"已删除 #{removed['id']}: {removed['title']}"


def compute_stats(todos: list[dict]) -> dict[str, float | int]:
    """统计总数、完成数、完成率。"""
    total = len(todos)
    done = sum(1 for t in todos if t["done"])
    rate = (done / total * 100) if total else 0.0
    return {"total": total, "done": done, "rate": rate}
