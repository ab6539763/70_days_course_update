# -*- coding: utf-8 -*-
"""Day 4 列表教学演示：CRUD、切片、排序、列表推导式。

运行：python3 list_demo.py

与课程衔接：
- Day 3 的 for/while 用于遍历列表
- Day 4 下午 todo_manager 用 list 存储 todos
- Day 15 将用 messages[-N:] 截取对话上下文
"""

from __future__ import annotations


def demo_create_and_len() -> None:
    """第一章：创建列表、len、成员检测。"""
    print("=== 创建与长度 ===")
    todos: list[str] = []
    todos.append("写接口文档")
    todos.append("补单元测试")
    print(f"todos = {todos}, len = {len(todos)}")
    print(f"'写接口文档' in todos -> {'写接口文档' in todos}")
    print(f"空列表 bool: {bool([])}, 非空: {bool(todos)}")


def demo_crud() -> None:
    """第二章：增删改查。"""
    print("\n=== CRUD ===")
    tasks: list[dict] = [
        {"id": 1, "title": "接口文档", "done": False},
        {"id": 2, "title": "单测", "done": False},
    ]

    # Create：尾部追加
    tasks.append({"id": 3, "title": "验收登录", "done": False})
    print(f"append 后: {[t['title'] for t in tasks]}")

    # Read：按下标与遍历
    print(f"tasks[0]['title'] = {tasks[0]['title']}")
    for i, t in enumerate(tasks, start=1):
        print(f"  {i}. #{t['id']} {t['title']}")

    # Update：修改字段
    tasks[1]["done"] = True
    print(f"完成第 2 项后 done 状态: {[t['done'] for t in tasks]}")

    # Delete：按索引删除
    removed = tasks.pop(0)
    print(f"pop(0) 删除: {removed['title']}, 剩余: {[t['title'] for t in tasks]}")


def demo_slicing() -> None:
    """第三章：切片（含头不含尾）。"""
    print("\n=== 切片 ===")
    messages = ["sys", "user1", "ai1", "user2", "ai2"]
    print(f"原列表: {messages}")
    print(f"前 2 条 [:2]     -> {messages[:2]}")
    print(f"最后 2 条 [-2:]   -> {messages[-2:]}")
    print(f"反转 [::-1]       -> {messages[::-1]}")
    print(f"步长 2 [::2]      -> {messages[::2]}")
    # 切片不改变原列表
    head = messages[:3]
    print(f"head 是副本，原列表仍为: {messages}")


def demo_sorting() -> None:
    """第四章：sort 原地排序 vs sorted 返回新列表。"""
    print("\n=== 排序 ===")
    nums = [3, 1, 4, 1, 5]
    ordered = sorted(nums)
    print(f"sorted(nums) -> {ordered}, 原 nums 不变: {nums}")

    nums_copy = nums[:]
    nums_copy.sort()
    print(f"nums.sort() 原地 -> {nums_copy}")

    todos = [
        {"id": 3, "title": "部署", "priority": "P2"},
        {"id": 1, "title": "接口", "priority": "P0"},
        {"id": 2, "title": "单测", "priority": "P1"},
    ]
    rank = {"P0": 0, "P1": 1, "P2": 2}
    by_priority = sorted(todos, key=lambda t: rank[t["priority"]])
    print("按优先级排序:")
    for t in by_priority:
        print(f"  {t['priority']} | {t['title']}")


def demo_comprehensions() -> None:
    """第五章：列表推导式与带条件过滤。"""
    print("\n=== 列表推导式 ===")
    squares = [x * x for x in range(6)]
    print(f"平方: {squares}")

    todos = [
        {"title": "A", "done": False},
        {"title": "B", "done": True},
        {"title": "C", "done": False},
    ]
    pending = [t["title"] for t in todos if not t["done"]]
    print(f"未完成标题: {pending}")

    # 嵌套：收集所有标签（作业会结合 set 去重）
    items = [
        {"tags": ["api", "doc"]},
        {"tags": ["api", "qa"]},
    ]
    all_tags = [tag for item in items for tag in item["tags"]]
    print(f"扁平标签: {all_tags}")


def main() -> None:
    demo_create_and_len()
    demo_crud()
    demo_slicing()
    demo_sorting()
    demo_comprehensions()
    print("\n演示结束。下一步请运行 tuple_set_demo.py 与 todo_manager.py。")


if __name__ == "__main__":
    main()
