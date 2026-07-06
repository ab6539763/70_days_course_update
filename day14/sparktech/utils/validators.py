# -*- coding: utf-8 -*-
"""字段校验与规范化工具。"""

from __future__ import annotations

import re

from sparktech.exceptions import ValidationError

_DIGITS_ONLY = re.compile(r"\D")


def strip_field(value: str) -> str:
    return value.strip()


def normalize_phone(phone: str) -> str:
    return _DIGITS_ONLY.sub("", phone.strip())


def validate_name(name: str) -> str:
    cleaned = strip_field(name)
    if not cleaned:
        raise ValidationError("姓名不能为空", field="name")
    return cleaned


def validate_phone(phone: str, *, min_digits: int = 7) -> str:
    digits = normalize_phone(phone)
    if len(digits) < min_digits:
        raise ValidationError(
            f"手机号至少 {min_digits} 位数字，当前 {len(digits)} 位",
            field="phone",
        )
    return digits
