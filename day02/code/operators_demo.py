# -*- coding: utf-8 -*-
"""Day 2 运算符教学演示。"""

from __future__ import annotations


def demo_arithmetic() -> None:
    print("=== 算术 ===")
    print(f"10 / 4 = {10 / 4} ({type(10 / 4).__name__})")
    print(f"10 // 4 = {10 // 4}")
    print(f"2 ** 10 = {2 ** 10} tokens 约 1K")


def demo_compare_logic() -> None:
    print("\n=== 比较与逻辑 ===")
    temp = 0.7
    print(f"temperature 合法: {0 <= temp <= 2}")
    cmd = "exit"
    print(f'cmd == "exit": {cmd == "exit"}')
    print(f'bool("") = {bool("")}, bool(" ") = {bool(" ")}')


def demo_api_cost() -> None:
    tokens = 12500
    price_per_1k = 0.002
    cost = tokens / 1000 * price_per_1k
    print(f"\n=== API 成本估算 ===\n{tokens} tokens -> {cost:.4f} 元")


def main() -> None:
    demo_arithmetic()
    demo_compare_logic()
    demo_api_cost()


if __name__ == "__main__":
    main()
