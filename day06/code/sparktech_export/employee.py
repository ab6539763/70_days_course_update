# -*- coding: utf-8 -*-
"""
星火科技 · Day 6 重构包 sparktech_export
模块：employee.py
说明：员工清洗与 JSON 导出（自 Day 5 export_employees_json.py 迁移）。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sparktech_cleaners import CaseMode, normalize_case, remove_all_spaces, strip_edges
from sparktech_onboard import DEFAULT_DEPARTMENT

from .api import parse_employees_from_file

_CODE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = _CODE_DIR / "output" / "employees_clean.json"

EXPORT_FIELDS: tuple[str, ...] = (
    "name",
    "employee_id",
    "department",
    "onboard_date",
    "phone",
    "need_dorm",
)


def clean_employee(raw: dict[str, Any]) -> dict[str, Any]:
    """将单条原始 employee dict 清洗为可入库格式。"""
    name = strip_edges(str(raw.get("name") or ""))
    employee_id = normalize_case(str(raw.get("employee_id") or ""), CaseMode.UPPER)
    department_raw = raw.get("department")
    if department_raw is None or str(department_raw).strip() == "":
        department = DEFAULT_DEPARTMENT
    else:
        department = strip_edges(str(department_raw))
    onboard_date = strip_edges(str(raw.get("onboard_date") or ""))
    phone = remove_all_spaces(str(raw.get("phone") or ""))
    need_dorm = bool(raw.get("need_dorm", False))
    return {
        "name": name,
        "employee_id": employee_id,
        "department": department,
        "onboard_date": onboard_date,
        "phone": phone,
        "need_dorm": need_dorm,
    }


def clean_all_employees(raw_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """批量清洗员工列表。"""
    return [clean_employee(item) for item in raw_list]


def write_employees_json(
    employees: list[dict[str, Any]],
    output_path: Path | str = OUTPUT_PATH,
) -> Path:
    """将清洗后的列表写入 JSON 文件。"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(employees, fp, ensure_ascii=False, indent=2)
    return path


def build_export_report(
    raw_list: list[dict[str, Any]],
    cleaned_list: list[dict[str, Any]],
    output_path: Path,
) -> str:
    """生成清洗统计报告文本（纯函数，不 print）。"""
    lines = [
        "=" * 60,
        "星火科技 · 员工 JSON 导出报告",
        "=" * 60,
        f"输入条数: {len(raw_list)}",
        f"输出条数: {len(cleaned_list)}",
        f"输出文件: {output_path}",
        "",
        "--- 清洗抽样 ---",
    ]
    for raw, clean in zip(raw_list, cleaned_list):
        changes: list[str] = []
        if raw.get("name") != clean.get("name"):
            changes.append(f"name: {raw.get('name')!r} -> {clean.get('name')!r}")
        if raw.get("employee_id") != clean.get("employee_id"):
            changes.append(
                f"employee_id: {raw.get('employee_id')!r} -> {clean.get('employee_id')!r}"
            )
        if raw.get("phone") != clean.get("phone"):
            changes.append(f"phone: {raw.get('phone')!r} -> {clean.get('phone')!r}")
        if raw.get("department") != clean.get("department"):
            changes.append(
                f"department: {raw.get('department')!r} -> {clean.get('department')!r}"
            )
        if changes:
            lines.append(f"  [{clean.get('employee_id')}] " + "; ".join(changes))
    lines.append("")
    lines.append("导出完成。")
    return "\n".join(lines)


def export_employees_from_mock(
    mock_path: Path | str | None = None,
    output_path: Path | str | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Path]:
    """完整流水线：解析 → 清洗 → 写文件。"""
    raw = parse_employees_from_file(mock_path)
    cleaned = clean_all_employees(raw)
    out = write_employees_json(cleaned, output_path or OUTPUT_PATH)
    return raw, cleaned, out
