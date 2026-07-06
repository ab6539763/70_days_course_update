# -*- coding: utf-8 -*-
"""
Day 3 主菜单壳 · 培训 CLI 统一入口。

PRD：S-01 ~ S-05
- 数字菜单分发子功能
- 斜杠命令：/exit /clear /help /history
- 预埋 Day 14 多轮对话助手的命令路由模式

运行：python3 simple_menu.py
"""

from __future__ import annotations

import sys

from constants import BANNER, MAIN_MENU, SLASH_COMMANDS

# 子模块 main 延迟导入，避免循环依赖并加快启动
import guess_number
import multiplication_table
import flow_control_demo


def clear_screen() -> None:
    """
    清屏：优先 ANSI 转义序列（现代终端 / SSH 通常支持）。

    Day 14 的 /clear 将改为 messages.clear()，函数名可复用。
    """
    print("\033[2J\033[H", end="")


def print_help() -> None:
    """打印斜杠命令与数字菜单说明。"""
    print("\n【斜杠命令】")
    for cmd, desc in SLASH_COMMANDS.items():
        print(f"  {cmd:<12} {desc}")
    print("\n【数字菜单】")
    for key, desc in MAIN_MENU.items():
        print(f"  {key}. {desc}")
    print("\n提示：命令与菜单可任选时刻输入；输入 /exit 立即退出。")


def print_main_menu() -> None:
    """显示主菜单横幅与选项。"""
    print(BANNER)
    for key, desc in MAIN_MENU.items():
        print(f"  {key}. {desc}")
    print("  任意时刻可输入 /help、/clear、/exit")


def dispatch_slash_command(raw: str) -> bool:
    """
    处理斜杠命令。

    Returns:
        True 表示应退出整个程序（/exit），False 表示继续 REPL。
    """
    cmd = raw.strip().lower()

    if cmd == "/exit":
        print("再见，期待 Day 14 星火智服助手上线！")
        return True

    if cmd == "/clear":
        clear_screen()
        print_main_menu()
        return False

    if cmd == "/help":
        print_help()
        return False

    if cmd == "/history":
        # Day 14：print(format_messages(messages))
        print("【历史】暂无对话记录。Day 14 将展示 messages 列表。")
        return False

    print(f"未知命令「{raw}」，输入 /help 查看可用命令。")
    return False


def dispatch_menu_choice(choice: str) -> None:
    """根据数字菜单调用子程序。"""
    if choice == "1":
        print("\n>>> 进入猜数字游戏（结束后返回主菜单）\n")
        guess_number.main()
    elif choice == "2":
        print("\n>>> 进入九九乘法表\n")
        multiplication_table.main()
    elif choice == "3":
        print("\n>>> 进入流程控制演示\n")
        flow_control_demo.main()
    elif choice == "4":
        print_help()
    else:
        print(f"无效菜单项「{choice}」。请输入 1-4 或 /help。")


def dispatch(raw: str) -> bool:
    """
    统一路由：先判断是否斜杠命令，再处理数字菜单。

    Returns:
        True 表示应退出主程序。
    """
    text = raw.strip()
    if not text:
        return False

    if text.startswith("/"):
        return dispatch_slash_command(text)

    dispatch_menu_choice(text)
    return False


def main() -> None:
    """
    REPL 主循环 —— Day 14 聊天助手将复用此结构：

        while True:
            raw = input(">>> ")
            if dispatch(raw):
                break
            # Day 14 else: 调用 API 并 append messages
    """
    print_main_menu()

    while True:
        try:
            raw = input("\n请输入菜单编号或命令: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n已中断，再见。")
            sys.exit(0)

        if dispatch(raw):
            break


if __name__ == "__main__":
    main()
