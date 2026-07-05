# -*- coding: utf-8 -*-
"""
星火科技 · 培训 Day 1
文件：personal_info_card.py
说明：入职信息卡片 v1.0 —— 满足 PRD-SPARK-ONBOARD-001 全部 P0 验收项。

需求追溯：
    AC-01  本文件可直接 python3 personal_info_card.py 运行
    AC-02  collect_inputs() 完成 6 字段交互
    AC-03  render_card() 输出与 PRD 原型一致
    AC-04  format_bool_display() 显示是/否
    AC-05  源码 UTF-8，中文标签见 constants
    AC-06  全文件中文注释

扩展路线：
    Day 5  增加 export_to_dict() -> json.dumps
    Day 6  函数已拆分，便于直接复用
    Day 11 增加 save_to_file(path)

作者：培训生（请修改）
日期：2026-07-05
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from constants import (
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
    """
    员工卡片数据载体。

    使用 dataclass 而非普通 dict 的原因（张工口述）：
        - 字段有自动补全，少写错 key
        - Day 8 会学 class，此处是温和过渡
        - Day 23 可一键改为 Pydantic BaseModel
    """

    name: str
    employee_id: str
    department: str
    onboard_date: str
    phone: str
    need_dorm: bool
    generated_at: str


def repeat_char(char: str, width: int) -> str:
    """
    生成分隔线字符串。

    Args:
        char: 重复的单字符，如 '=' 或 '-'
        width: 总宽度

    Returns:
        长度为 width 的字符串
    """
    return char * width


def format_bool_display(value: bool) -> str:
    """
    将布尔值映射为 PRD 要求的中文展示。

    PRD AC-04：界面不得出现 True/False 英文字样给业务方查看。
    """
    return BOOL_DISPLAY_TRUE if value else BOOL_DISPLAY_FALSE


def parse_need_dorm(raw: str) -> bool:
    """
    解析用户输入的住宿意愿。

    容忍大小写与常见中英文肯定词。v1.0 不做循环重输，Day 3 用 while 加强。

    Args:
        raw: input() 返回的原始字符串

    Returns:
        True 表示需要住宿
    """
    normalized = raw.strip().lower()
    return normalized in ("y", "yes", "是", "1", "要")


def collect_inputs() -> EmployeeCard:
    """
    从终端依次采集 PRD 3.1 节定义的六个字段。

    Returns:
        填充完毕的 EmployeeCard（generated_at 在 render 前生成）
    """
    print()
    print(f"欢迎加入{COMPANY_NAME}！请按提示填写入职信息。")
    print(repeat_char(LINE_CHAR_SUB, CARD_WIDTH))
    print()

    # --- 姓名 ---
    name = input(PROMPT_NAME).strip()
    # v1.0：若为空暂用占位，Day 3 改为 while not name 循环
    if not name:
        name = "（未填写）"

    # --- 工号：允许回车使用示例工号（US-04）---
    employee_id = input(PROMPT_EMPLOYEE_ID).strip()
    if not employee_id:
        employee_id = SAMPLE_EMPLOYEE_ID

    # --- 部门 ---
    department = input(PROMPT_DEPARTMENT).strip()
    if not department:
        department = DEFAULT_DEPARTMENT

    # --- 入职日期 ---
    onboard_date = input(PROMPT_ONBOARD_DATE).strip()
    if not onboard_date:
        # 默认今天，减少演示时手工输入
        onboard_date = datetime.now().strftime("%Y-%m-%d")

    # --- 手机号：强制 str，避免 int 丢失前导零 ---
    phone = input(PROMPT_PHONE).strip()
    if not phone:
        phone = "（未填写）"

    # --- 是否住宿 ---
    need_dorm_raw = input(PROMPT_NEED_DORM)
    need_dorm = parse_need_dorm(need_dorm_raw)

    # generated_at 在展示前才定格，此处先占位
    return EmployeeCard(
        name=name,
        employee_id=employee_id,
        department=department,
        onboard_date=onboard_date,
        phone=phone,
        need_dorm=need_dorm,
        generated_at="",
    )


def render_card(card: EmployeeCard) -> str:
    """
    将 EmployeeCard 渲染为固定版式字符串。

    同时返回字符串而非仅 print 的原因：
        Day 11 会调用本函数返回值写入 txt 文件
        Day 34 评估报告也会用「先拼字符串再输出」模式

    Args:
        card: 员工数据

    Returns:
        完整卡片文本（含末尾换行）
    """
    # 在最后一刻记录生成时间，保证与「打印时刻」一致
    card.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    main_line = repeat_char(LINE_CHAR_MAIN, CARD_WIDTH)
    sub_line = repeat_char(LINE_CHAR_SUB, CARD_WIDTH)

    # 使用列表收集各行，最后用 join 拼接，比多次 print 更易测
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
        "",  # 末尾空行，终端阅读更舒适
    ]
    return "\n".join(lines)


def main() -> None:
    """主流程：采集 -> 渲染 -> 输出。"""
    card = collect_inputs()
    output = render_card(card)
    print()
    print(output)


if __name__ == "__main__":
    main()
