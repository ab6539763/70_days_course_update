# -*- coding: utf-8 -*-
"""
Day 3 流程控制语法演示。

分四段演示 if/elif/else、嵌套条件、while、for+range、break/continue。
适合讲师投屏分段讲解；每段结束等待回车继续。

运行：python3 flow_control_demo.py
"""

from __future__ import annotations


def demo_if_elif_else() -> None:
    """第一段：成绩等级 —— if / elif / else 链。"""
    print("\n" + "=" * 50)
    print("【演示 1】if / elif / else · 成绩等级")
    print("=" * 50)

    raw = input("请输入成绩 (0-100): ").strip()
    if not raw.isdigit():
        print("非数字输入，演示结束本段。")
        return

    score = int(raw)
    # elif 链：自上而下，只执行第一个为真的分支
    if score >= 90:
        grade = "A"
        remark = "优秀"
    elif score >= 80:
        grade = "B"
        remark = "良好"
    elif score >= 60:
        grade = "C"
        remark = "及格"
    else:
        grade = "D"
        remark = "需补考"

    print(f"成绩 {score} → 等级 {grade}（{remark}）")

    # 嵌套条件：初试不及格时再看补考
    if score < 60:
        makeup_raw = input("补考成绩 (0-100，直接回车跳过): ").strip()
        if makeup_raw.isdigit():
            makeup = int(makeup_raw)
            if makeup >= 60:
                print(f"补考 {makeup} 分，视为通过。")
            else:
                print("补考仍未及格，建议重修。")
        else:
            print("未录入补考成绩。")


def demo_while_retry() -> None:
    """第二段：while 循环 · 修复 Day 1 空姓名问题。"""
    print("\n" + "=" * 50)
    print("【演示 2】while · 非空输入重试（Day 1 卡片改进）")
    print("=" * 50)

    name = ""
    # 条件为假时退出；这里用「非 name」即空串时继续循环
    while not name.strip():
        name = input("姓名（不能为空）: ")
        if not name.strip():
            print("  → 检测到空输入，请重新填写。")

    print(f"欢迎，{name.strip()}！已写入（模拟）入职卡片。")


def demo_for_range() -> None:
    """第三段：for + range · 遍历与九九表一行。"""
    print("\n" + "=" * 50)
    print("【演示 3】for + range · 遍历部门与乘法口诀")
    print("=" * 50)

    departments = ["大模型应用开发部", "算法部", "产品部"]
    print("enumerate 风格遍历：")
    for index in range(len(departments)):
        # range(len) 生成 0,1,2... 下标；Day 4 可直接 for dept in departments
        print(f"  {index + 1}. {departments[index]}")

    print("\n九九表第 7 行（j 从 1 到 i）：")
    row = 7
    for j in range(1, row + 1):
        print(f"  {row}×{j}={row * j}", end="  ")
    print()


def demo_break_continue() -> None:
    """第四段：break 与 continue 对比。"""
    print("\n" + "=" * 50)
    print("【演示 4】break vs continue")
    print("=" * 50)

    print("仅打印 1~10 中的奇数，遇到 7 时 break（不打印 7）：")
    for i in range(1, 11):
        if i % 2 == 0:
            continue  # 跳过偶数，进入下一轮 i
        if i == 7:
            break  # 整个 for 结束
        print(f"  {i}", end="")
    print("\n")

    print("模拟猜数字：非法输入 continue 不占次数，猜中 break")
    secret = 5
    attempt = 0
    max_try = 5
    while attempt < max_try:
        raw = input(f"猜 1-10 的整数（第 {attempt + 1}/{max_try} 次）: ").strip()
        if not raw.isdigit():
            print("  → 非法输入，不计次数，continue")
            continue
        guess = int(raw)
        attempt += 1
        if guess < secret:
            print("  太小")
        elif guess > secret:
            print("  太大")
        else:
            print("  猜中了！break 退出循环")
            break
    else:
        # for/while 的 else：未 break 时执行
        print(f"  次数用尽，答案是 {secret}")


def main() -> None:
    """按顺序运行四段演示。"""
    print("星火科技 Day 3 · flow_control_demo")
    print("每段结束按回车继续下一段。")

    demo_if_elif_else()
    input("\n按回车继续 → 演示 2 ...")

    demo_while_retry()
    input("\n按回车继续 → 演示 3 ...")

    demo_for_range()
    input("\n按回车继续 → 演示 4 ...")

    demo_break_continue()
    print("\n四段演示结束。请运行 guess_number.py / simple_menu.py 完成实操。")


if __name__ == "__main__":
    main()
