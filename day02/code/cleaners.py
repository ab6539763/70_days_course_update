# -*- coding: utf-8 -*-
"""
Day 2 清洗函数库。
每个函数：输入 str -> 输出 str，无副作用，便于 Day 6 单测与 Day 28 复用。
"""

from __future__ import annotations

import re
from pathlib import Path

from constants import CaseMode, DEFAULT_SENSITIVE_FILE


def strip_edges(text: str) -> str:
    """PRD F-01：去除首尾空白字符（含 \\n \\t）。"""
    return text.strip()


def collapse_spaces(text: str) -> str:
    """
    PRD F-02：将任意连续空白（空格/制表/换行）压缩为单个空格。

    使用 re.sub 预习 Day 11 正则；作业 C1 要求用 split+join 手写一版对比。
    """
    return re.sub(r"\s+", " ", text.strip())


def remove_all_spaces(text: str) -> str:
    """PRD F-05：删除全部空白，适用于手机号等字段。"""
    return "".join(text.split())


def normalize_case(text: str, mode: CaseMode | str = CaseMode.KEEP) -> str:
    """PRD F-03：按模式转换大小写。"""
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
    """从词表文件加载敏感词，一行一词，# 开头为注释。"""
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
    """
    PRD F-04：敏感词等长替换。

    v1.0 简单 replace 链；词表量大时 Day 11 可用 re 编译一次。
    """
    if not words:
        words = load_sensitive_words()
    result = text
    for word in words:
        if not word:
            continue
        replacement = mask_char * len(word)
        result = result.replace(word, replacement)
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
    """
    按顺序执行清洗步骤。顺序设计：先结构空白，再大小写，最后敏感词。
    """
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
