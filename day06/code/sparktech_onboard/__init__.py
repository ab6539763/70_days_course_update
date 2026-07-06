# -*- coding: utf-8 -*-
"""入职信息卡片包：Day 1 脚本重构后的可复用函数。"""

from .card import (
    EmployeeCard,
    card_to_dict,
    collect_inputs,
    format_bool_display,
    parse_need_dorm,
    render_card,
    repeat_char,
)
from .constants import DEFAULT_DEPARTMENT, COMPANY_NAME

__all__ = [
    "COMPANY_NAME",
    "DEFAULT_DEPARTMENT",
    "EmployeeCard",
    "card_to_dict",
    "collect_inputs",
    "format_bool_display",
    "parse_need_dorm",
    "render_card",
    "repeat_char",
]
