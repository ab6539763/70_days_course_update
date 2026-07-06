# -*- coding: utf-8 -*-
"""
Day 3 九九乘法表生成器。

PRD：M-01 ~ M-04
- 双重 for 打印下三角标准表
- 支持指定行
- f-string 对齐输出

运行：python3 multiplication_table.py
"""

from __future__ import annotations


def print_row(n: int) -> None:
    """
    打印乘法表第 n 行（1 ≤ n ≤ 9）。

    内层 j 从 1 到 n，体现「列号不超过行号」的下三角规律。
    """
    if not 1 <= n <= 9:
        print(f"  行号 {n} 无效，应在 1~9 之间。")
        return

    parts: list[str] = []
    for j in range(1, n + 1):
        # 固定宽度便于投屏对齐；\t 在部分终端也可
        parts.append(f"{n}×{j}={n * j}")
    print("  " + "  ".join(parts))


def print_full_table() -> None:
    """打印完整 9×9 下三角乘法表（PRD M-01）。"""
    print("\n—— 标准九九乘法表 ——\n")
    for i in range(1, 10):
        print_row(i)


def read_menu_choice() -> str:
    """读取菜单选项，允许空行时由调用方处理默认值。"""
    return input("\n请选择 [0]: ").strip()


def read_row_number() -> int | None:
    """读取指定行号，非法则返回 None。"""
    raw = input("请输入行号 (1-9): ").strip()
    if not raw.isdigit():
        print("  请输入整数。")
        return None
    n = int(raw)
    if 1 <= n <= 9:
        return n
    print("  行号应在 1~9 之间。")
    return None


def print_menu() -> None:
    """显示子菜单。"""
    print("\n=== 九九乘法表 ===")
    print("  1. 打印完整乘法表")
    print("  2. 打印指定行")
    print("  0. 返回上级 / 退出")


def main() -> None:
    """菜单循环，直到用户选择 0。"""
    print("星火科技 · 九九乘法表工具 v1.0")

    while True:
        print_menu()
        choice = read_menu_choice() or "0"

        if choice == "0":
            print("再见。")
            break
        if choice == "1":
            print_full_table()
        elif choice == "2":
            n = read_row_number()
            if n is not None:
                print_row(n)
        else:
            print("  无效选项，请重新选择。")


if __name__ == "__main__":
    main()
