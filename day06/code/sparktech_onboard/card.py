# -*- coding: utf-8 -*-
"""
星火科技 · Day 6 重构包 sparktech_onboard
模块：card.py
说明：入职信息卡片纯函数（自 Day 1 personal_info_card.py 拆分）。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .constants import (
    BOOL_DISPLAY_FALSE,
    BOOL_DISPLAY_TRUE,
    CARD_SUBTITLE,
    CARD_WIDTH,
    COMPANY_NAME,
    DEFAULT_DEPARTMENT,
    LINE_CHAR_MAIN,
    LINE_CHAR_SUB,
    PROMPT_DEPARTMENT,
    PROMPT_EMPLOYEE_ID,
    PROMPT_NAME,
    PROMPT_NEED_DORM,
    PROMPT_ONBOARD_DATE,
    PROMPT_PHONE,
    SAMPLE_EMPLOYEE_ID,
)


@dataclass
class EmployeeCard:
    """员工卡片数据载体。"""

    name: str
    employee_id: str
    department: str
    onboard_date: str
    phone: str
    need_dorm: bool
    generated_at: str = ""


def repeat_char(char: str, width: int) -> str:
    """生成分隔线字符串。"""
    return char * width


def format_bool_display(value: bool) -> str:
    """将布尔值映射为中文「是/否」。"""
    return BOOL_DISPLAY_TRUE if value else BOOL_DISPLAY_FALSE


def parse_need_dorm(raw: str) -> bool:
    """解析用户输入的住宿意愿。"""
    normalized = raw.strip().lower()
    return normalized in ("y", "yes", "是", "1", "要")


def collect_inputs() -> EmployeeCard:
    """从终端依次采集六个字段，返回 EmployeeCard。"""
    print()
    print(f"欢迎加入{COMPANY_NAME}！请按提示填写入职信息。")
    print(repeat_char(LINE_CHAR_SUB, CARD_WIDTH))
    print()

    name = input(PROMPT_NAME).strip() or "（未填写）"
    employee_id = input(PROMPT_EMPLOYEE_ID).strip() or SAMPLE_EMPLOYEE_ID
    department = input(PROMPT_DEPARTMENT).strip() or DEFAULT_DEPARTMENT
    onboard_date = input(PROMPT_ONBOARD_DATE).strip() or datetime.now().strftime("%Y-%m-%d")
    phone = input(PROMPT_PHONE).strip() or "（未填写）"
    need_dorm = parse_need_dorm(input(PROMPT_NEED_DORM))

    return EmployeeCard(
        name=name,
        employee_id=employee_id,
        department=department,
        onboard_date=onboard_date,
        phone=phone,
        need_dorm=need_dorm,
    )


def card_to_dict(card: EmployeeCard) -> dict[str, str | bool]:
    """将卡片转为 dict，供 Day 5 JSON 导出复用。"""
    return {
        "name": card.name,
        "employee_id": card.employee_id,
        "department": card.department,
        "onboard_date": card.onboard_date,
        "phone": card.phone,
        "need_dorm": card.need_dorm,
    }


def render_card(card: EmployeeCard) -> str:
    """将 EmployeeCard 渲染为固定版式字符串。"""
    card.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    main_line = repeat_char(LINE_CHAR_MAIN, CARD_WIDTH)
    sub_line = repeat_char(LINE_CHAR_SUB, CARD_WIDTH)
    lines: list[str] = [
        main_line,
        f"{COMPANY_NAME} · {CARD_SUBTITLE}".center(CARD_WIDTH),
        main_line,
        f"  姓    名：{card.name}",
        f"  工    号：{card.employee_id}",
        f"  部    门：{card.department}",
        f"  入职日期：{card.onboard_date}",
        f"  联系电话：{card.phone}",
        f"  是否住宿：{format_bool_display(card.need_dorm)}",
        sub_line,
        f"  生成时间：{card.generated_at}",
        main_line,
        "",
    ]
    return "\n".join(lines)
