# -*- coding: utf-8 -*-
"""Day 6 重构包 sparktech_cleaners 常量（自 Day 2 迁移）。"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent


class CaseMode(str, Enum):
    """大小写转换模式。"""

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

DEFAULT_SENSITIVE_FILE = _PACKAGE_DIR / "data" / "sensitive_words.txt"
