# -*- coding: utf-8 -*-
"""
Day 3 猜数字培训游戏。

PRD：G-01 ~ G-05
- random.randint 生成目标
- while/for 控制回合
- 非法输入 continue 不计次
- 猜中 break；可再来一局

运行：python3 guess_number.py
"""

from __future__ import annotations

import random

from constants import GUESS_MAX, GUESS_MIN, MAX_ATTEMPTS


def read_valid_int(prompt: str) -> int:
    """
    循环读取合法整数。

    使用 while True + continue，直到用户输入整数字符串。
    Day 8 将改用 try/except ValueError。
    """
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("  输入不能为空，请重试。")
            continue
        # str.isdigit() 仅适用于非负整数；负数场景需另写逻辑
        if not raw.isdigit():
            print("  请输入正整数。")
            continue
        return int(raw)


def play_round(
    low: int = GUESS_MIN,
    high: int = GUESS_MAX,
    max_attempts: int = MAX_ATTEMPTS,
) -> bool:
    """
    进行一局猜数字。

    Returns:
        True 表示用户猜中，False 表示次数用尽。
    """
    secret = random.randint(low, high)
    print(f"\n—— 新一局开始（范围 {low}~{high}，最多 {max_attempts} 次）——")
    print("（讲师提示：secret 已生成，学员请勿偷看屏幕调试输出）")

    # for-else：循环正常结束（未 break）时执行 else
    for attempt in range(1, max_attempts + 1):
        guess = read_valid_int(f"第 {attempt}/{max_attempts} 次猜测: ")

        if guess < secret:
            print("  📉 太小了")
        elif guess > secret:
            print("  📈 太大了")
        else:
            print(f"  🎉 恭喜！{guess} 就是答案，用了 {attempt} 次。")
            return True
    else:
        print(f"  😢 次数用尽。正确答案是 {secret}。")
        return False


def ask_play_again() -> bool:
    """询问是否再来一局；y/yes/是 继续，其余退出。"""
    while True:
        raw = input("\n再来一局？(y/n) [n]: ").strip().lower()
        if raw in ("", "n", "no", "否"):
            return False
        if raw in ("y", "yes", "是"):
            return True
        print("  请输入 y 或 n。")


def main() -> None:
    """主循环：多局游戏，直到用户选择不再继续。"""
    print("=" * 50)
    print("  星火科技 · 集训破冰 · 猜数字 v1.0")
    print("=" * 50)
    print(f"规则：心里想好一个 {GUESS_MIN}~{GUESS_MAX} 的数……")
    print("      哦不对，是程序想好，你来猜。")

    # 外层 while：控制「是否再来一局」
    while True:
        play_round()
        if not ask_play_again():
            print("\n感谢参与集训小游戏，再见！")
            break


if __name__ == "__main__":
    main()
