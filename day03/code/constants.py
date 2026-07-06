# -*- coding: utf-8 -*-
"""Day 3 常量：菜单文案、命令列表、游戏默认参数。"""

from __future__ import annotations

# 猜数字默认最大尝试次数（PRD G-02）
MAX_ATTEMPTS: int = 7

# 随机数默认范围
GUESS_MIN: int = 1
GUESS_MAX: int = 100

# 主菜单数字选项（simple_menu.py）
MAIN_MENU: dict[str, str] = {
    "1": "猜数字培训游戏",
    "2": "九九乘法表",
    "3": "流程控制语法演示",
    "4": "帮助说明",
}

# 斜杠命令 —— 与 Day 14 命令行 AI 助手保持一致的前缀约定
SLASH_COMMANDS: dict[str, str] = {
    "/exit": "退出程序",
    "/clear": "清屏",
    "/help": "显示命令与菜单帮助",
    "/history": "对话历史（Day 14 实现，当前为占位）",
}

BANNER: str = """
╔══════════════════════════════════════════════════╗
║     星火科技 · 星火智服 · 内部培训 CLI v1.0      ║
║     Day 3 分支与循环 · 菜单壳预埋 /clear /exit   ║
╚══════════════════════════════════════════════════╝
"""
