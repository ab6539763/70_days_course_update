# -*- coding: utf-8 -*-
"""
星火科技 · Day 6 重构包 sparktech_onboard
模块：constants.py
说明：入职信息卡片业务常量（自 Day 1 迁移，供包内模块 import）。
"""

COMPANY_NAME: str = "星火科技"
CARD_SUBTITLE: str = "入职信息卡片"
CARD_WIDTH: int = 50
LINE_CHAR_MAIN: str = "="
LINE_CHAR_SUB: str = "-"

DEPARTMENTS: tuple[str, ...] = (
    "大模型应用开发部",
    "智能应用事业部-交付组",
    "智能应用事业部-产品组",
    "人力资源部",
    "信息技术部",
)
DEFAULT_DEPARTMENT: str = "大模型应用开发部"

EMPLOYEE_ID_PREFIX: str = "ST"
SAMPLE_EMPLOYEE_ID: str = "ST-2026-001"

PROMPT_NAME: str = "请输入姓名（2-20字）："
PROMPT_EMPLOYEE_ID: str = "请输入工号（如 ST-2026-001，直接回车使用示例工号）："
PROMPT_DEPARTMENT: str = "请输入部门（直接回车使用默认部门）："
PROMPT_ONBOARD_DATE: str = "请输入入职日期（YYYY-MM-DD）："
PROMPT_PHONE: str = "请输入 11 位手机号："
PROMPT_NEED_DORM: str = "是否住宿？(y/n)："

BOOL_DISPLAY_TRUE: str = "是"
BOOL_DISPLAY_FALSE: str = "否"
