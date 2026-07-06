# -*- coding: utf-8 -*-
"""Day 2 常量：清洗选项与菜单文案。"""

from __future__ import annotations

from enum import Enum


class CaseMode(str, Enum):
    """PRD F-03 大小写模式。"""

    KEEP = "keep"
    LOWER = "lower"
    UPPER = "upper"
    TITLE = "title"


MENU_OPTIONS: dict[str, str] = {
    "1": "去除首尾空白 (strip)",
    "2": "合并连续空白 (collapse)",
    "3": "统一大小写 (case)",
    "4": "敏感词替换 (mask)",
    "5": "删除所有空白 (remove_all)",
}

DEFAULT_SENSITIVE_FILE = "data/sensitive_words.txt"
