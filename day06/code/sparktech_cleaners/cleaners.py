# -*- coding: utf-8 -*-
"""
Day 6 重构包 sparktech_cleaners
说明：字符串清洗纯函数（自 Day 2 cleaners.py 迁移，包内相对导入）。
"""

from __future__ import annotations

import re
from pathlib import Path

from .constants import CaseMode, DEFAULT_SENSITIVE_FILE


def strip_edges(text: str) -> str:
    """去除首尾空白字符。"""
    return text.strip()


def collapse_spaces(text: str) -> str:
    """将连续空白压缩为单个空格。"""
    return re.sub(r"\s+", " ", text.strip())


def remove_all_spaces(text: str) -> str:
    """删除全部空白。"""
    return "".join(text.split())


def normalize_case(text: str, mode: CaseMode | str = CaseMode.KEEP) -> str:
    """按模式转换大小写。"""
    if isinstance(mode, str):
        mode = CaseMode(mode)
    if mode == CaseMode.LOWER:
        return text.lower()
    if mode == CaseMode.UPPER:
        return text.upper()
    if mode == CaseMode.TITLE:
        return text.title()
    return text


def load_sensitive_words(path: str | Path | None = None) -> list[str]:
    """从词表文件加载敏感词。"""
    file_path = Path(path or DEFAULT_SENSITIVE_FILE)
    if not file_path.is_file():
        return ["傻瓜", "笨蛋", "违禁测试词"]
    words: list[str] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            words.append(line)
    return words


def mask_sensitive(
    text: str,
    words: list[str] | None = None,
    mask_char: str = "*",
) -> str:
    """敏感词等长替换。"""
    if not words:
        words = load_sensitive_words()
    result = text
    for word in words:
        if not word:
            continue
        result = result.replace(word, mask_char * len(word))
    return result


def apply_pipeline(
    text: str,
    *,
    do_strip: bool = False,
    do_collapse: bool = False,
    do_remove_all: bool = False,
    case_mode: CaseMode = CaseMode.KEEP,
    do_mask: bool = False,
    sensitive_words: list[str] | None = None,
) -> str:
    """按顺序执行清洗步骤。"""
    result = text
    if do_strip:
        result = strip_edges(result)
    if do_remove_all:
        result = remove_all_spaces(result)
    elif do_collapse:
        result = collapse_spaces(result)
    result = normalize_case(result, case_mode)
    if do_mask:
        result = mask_sensitive(result, sensitive_words)
    return result
