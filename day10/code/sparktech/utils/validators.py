# -*- coding: utf-8 -*-
"""字段校验与规范化工具。"""

from __future__ import annotations

import re

from sparktech.exceptions import ValidationError

_DIGITS_ONLY = re.compile(r"\D")


def strip_field(value: str) -> str:
    """去除首尾空白。"""
    return value.strip()


def normalize_phone(phone: str) -> str:
    """去掉空格与连字符，仅保留数字。"""
    return _DIGITS_ONLY.sub("", phone.strip())


def validate_name(name: str) -> str:
    """校验姓名非空，返回 strip 后的值。"""
    cleaned = strip_field(name)
    if not cleaned:
        raise ValidationError("姓名不能为空", field="name")
    return cleaned


def validate_phone(phone: str, *, min_digits: int = 7) -> str:
    """校验手机号位数，返回规范化后的数字串。"""
    digits = normalize_phone(phone)
    if len(digits) < min_digits:
        raise ValidationError(
            f"手机号至少 {min_digits} 位数字，当前 {len(digits)} 位",
            field="phone",
        )
    return digits
