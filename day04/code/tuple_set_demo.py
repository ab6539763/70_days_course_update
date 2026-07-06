# -*- coding: utf-8 -*-
"""Day 4 元组与集合教学演示。

运行：python3 tuple_set_demo.py

业务场景：
- tuple：不可变配置、函数多返回值、作为 dict 的 key
- set：标签去重、成员检测、集合交并差（RAG 文档 id 过滤预习）
"""

from __future__ import annotations


# 优先级顺序用 tuple：防止运行中被 append 篡改
PRIORITY_ORDER: tuple[str, ...] = ("P0", "P1", "P2")


def demo_tuple() -> None:
    """第六章：元组不可变、打包解包、多返回值。"""
    print("=== 元组 tuple ===")
    point = (10, 20)
    print(f"坐标 point = {point}, x = {point[0]}")

    # 单元素 tuple 必须有逗号
    single = (42,)
    print(f"单元素: {single}, 类型: {type(single).__name__}")

    # 解包
    name, year = ("星火科技", 2026)
    print(f"解包: {name} / {year}")

    # 函数返回多个值（本质是 tuple）
    todos, next_id = _mock_load()
    print(f"多返回值: todos={todos}, next_id={next_id}")

    # tuple 作为 dict 的 key（list 不行，因为 list 不可哈希）
    cache: dict[tuple[str, float], str] = {}
    cache[("gpt-4", 0.7)] = "某次回答摘要"
    print(f"缓存 key ('gpt-4', 0.7): {cache[('gpt-4', 0.7)]}")

    # 不可变演示（取消注释会报错）
    # point[0] = 5  # TypeError: 'tuple' object does not support item assignment


def _mock_load() -> tuple[list[str], int]:
    """模拟 Day 5 从 JSON 加载后返回 (todos, next_id)。"""
    return ["任务A", "任务B"], 3


def demo_set() -> None:
    """第七章：集合去重与交并差。"""
    print("\n=== 集合 set ===")
    raw_tags = ["api", "doc", "api", "qa", ""]
    cleaned = {t for t in raw_tags if t}  # 去重且过滤空串
    print(f"标签去重: {cleaned}")

    ids = set([101, 102, 102, 103])
    print(f"文档 id 集合: {ids}, 102 in ids -> {102 in ids}")

    team_a = {"api", "doc", "frontend"}
    team_b = {"api", "qa", "ops"}
    print(f"并集 A|B: {team_a | team_b}")
    print(f"交集 A&B: {team_a & team_b}")
    print(f"差集 A-B: {team_a - team_b}")


def demo_parse_tags(raw: str) -> list[str]:
    """PRD V-04：逗号分隔标签 → set 去重 → 排序列表便于展示。"""
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return sorted(set(parts))


def demo_tuple_in_todo() -> None:
    """结合待办业务：优先级校验与标签解析。"""
    print("\n=== 业务结合 ===")
    user_priority = "PX"
    if user_priority not in PRIORITY_ORDER:
        user_priority = "P1"
        print(f"非法优先级，回退为 {user_priority}")

    tags = demo_parse_tags("api, doc, api, qa")
    print(f"parse_tags('api, doc, api, qa') -> {tags}")


def main() -> None:
    demo_tuple()
    demo_set()
    demo_tuple_in_todo()
    print("\n演示结束。请运行 todo_manager.py 完成今日实操。")


if __name__ == "__main__":
    main()
