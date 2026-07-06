# -*- coding: utf-8 -*-
"""
Day 6 课堂演示：函数定义、参数、返回值、作用域、lambda、递归入门。
运行：cd day06/code && python3 demo_functions.py
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# 第一章：函数定义与返回值
# ---------------------------------------------------------------------------


def greet(name: str, company: str = "星火科技") -> str:
    """位置参数 + 默认参数 + 返回值。"""
    return f"欢迎加入{company}，{name}！"


def build_employee_line(name: str, employee_id: str, *, department: str) -> str:
    """keyword-only 参数：* 之后的参数必须用关键字传递。"""
    return f"{name} | {employee_id} | {department}"


def sum_numbers(*args: int) -> int:
    """*args：收集任意个位置参数为元组。"""
    return sum(args)


def merge_config(**kwargs: str) -> dict[str, str]:
    """**kwargs：收集任意个关键字参数为字典。"""
    return dict(kwargs)


# ---------------------------------------------------------------------------
# 第二章：作用域
# ---------------------------------------------------------------------------

COMPANY = "星火科技"  # 模块级全局


def outer_counter() -> callable:
    """闭包：内部函数记住外层局部变量。"""
    count = 0

    def increment(step: int = 1) -> int:
        nonlocal count
        count += step
        return count

    return increment


def demo_scope() -> None:
  """演示 LEGB 查找顺序。"""
  prefix = "[局部]"

  def inner() -> str:
      return f"{prefix} {COMPANY}"

  print(inner())


# ---------------------------------------------------------------------------
# 第三章：lambda 与高阶函数
# ---------------------------------------------------------------------------

PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2}

SAMPLE_TODOS = [
    {"id": 1, "title": "写 Day6 讲义", "priority": "P0", "done": False},
    {"id": 2, "title": "重构 cleaners", "priority": "P1", "done": True},
    {"id": 3, "title": "Code Review", "priority": "P2", "done": False},
]


def sort_by_priority(todos: list[dict]) -> list[dict]:
    """lambda 作为 sorted 的 key 函数。"""
    return sorted(todos, key=lambda t: PRIORITY_RANK.get(t["priority"], 9))


def filter_undone(todos: list[dict]) -> list[dict]:
    """filter + lambda。"""
    return list(filter(lambda t: not t["done"], todos))


# ---------------------------------------------------------------------------
# 第四章：递归入门
# ---------------------------------------------------------------------------


def factorial(n: int) -> int:
    """阶乘：经典递归（课堂版，n 较小时安全）。"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def flatten_once(nested: list) -> list:
    """
    只展开一层嵌套列表。
    Day 28 会处理任意深度；今日理解「基线条件 + 递归步」即可。
    """
    result: list = []
    for item in nested:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result


def main() -> None:
    print("=" * 50)
    print("Day 6 · 函数与作用域演示")
    print("=" * 50)

    print("\n[1] 默认参数与返回值")
    print(greet("陈晓"))
    print(greet("李雷", company="星火智服"))

    print("\n[2] keyword-only 参数")
    print(build_employee_line("韩梅梅", "ST-2026-004", department="大模型应用开发部"))

    print("\n[3] *args / **kwargs")
    print("sum_numbers(1,2,3,4) =", sum_numbers(1, 2, 3, 4))
    print("merge_config =", merge_config(model="qwen", temperature="0.7"))

    print("\n[4] 作用域与闭包")
    demo_scope()
    counter = outer_counter()
    print("counter:", counter(), counter(), counter(5))

    print("\n[5] lambda 排序与过滤")
    for item in sort_by_priority(SAMPLE_TODOS):
        print(" ", item["priority"], item["title"])
    print("未完成:", [t["title"] for t in filter_undone(SAMPLE_TODOS)])

    print("\n[6] 递归")
    print("factorial(5) =", factorial(5))
    print("flatten_once =", flatten_once([1, [2, 3], 4, [5]]))

    print("\n演示结束。下午实操请运行 run_export_json.py 验证包重构。")


if __name__ == "__main__":
    main()
