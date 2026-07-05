# -*- coding: utf-8 -*-
"""
星火科技 · 培训 Day 5
文件：export_employees_json.py
说明：解析 Mock API → 调用 Day 2 清洗函数 → 导出标准 JSON 文件。

需求追溯（PRD-SPARK-JSON-005）：
    E-01  字段清洗（strip / upper / remove_all_spaces）
    E-02  department 为 null 时填默认部门
    E-03  输出 code/output/employees_clean.json
    E-04  ensure_ascii=False, indent=2
    E-05  控制台统计报告

业务链：
    Day 1 字段 schema → Day 2 cleaners → Day 5 本脚本 → 王工测试库

作者：培训生（请修改）
日期：2026-07-10
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 导入 Day 2 清洗模块（复用 PRD-SPARK-CLEAN-002，禁止复制粘贴实现）
# ---------------------------------------------------------------------------
CODE_DIR = Path(__file__).resolve().parent
DAY02_CODE = CODE_DIR.parents[1] / "day02" / "code"
if str(DAY02_CODE) not in sys.path:
    sys.path.insert(0, str(DAY02_CODE))

from cleaners import normalize_case, remove_all_spaces, strip_edges  # noqa: E402
from constants import CaseMode  # noqa: E402

from parse_api import parse_employees_from_file  # noqa: E402

# ---------------------------------------------------------------------------
# 业务常量
# ---------------------------------------------------------------------------

# 与 Day 1 constants.DEFAULT_DEPARTMENT 保持一致
DEFAULT_DEPARTMENT = "大模型应用开发部"

# 导出文件路径（PRD E-03）
OUTPUT_PATH = CODE_DIR / "output" / "employees_clean.json"

# 导出 JSON 的字段顺序，便于人工 diff 与信息科导入映射
EXPORT_FIELDS: tuple[str, ...] = (
    "name",
    "employee_id",
    "department",
    "onboard_date",
    "phone",
    "need_dorm",
)


def clean_employee(raw: dict[str, Any]) -> dict[str, Any]:
    """
    将单条原始 employee dict 清洗为可入库格式。

    设计原则：
        - 返回新 dict，不修改 raw（保留原始数据便于对比）
        - 所有字符串字段用 or "" 防御 None
        - 布尔字段保持 bool 类型，JSON 导出时为 true/false

    参数:
        raw: Mock API 中的单条员工记录

    返回:
        字段完整、已清洗的 dict
    """
    # 姓名字段：去除首尾空白（Day 2 F-01）
    name = strip_edges(str(raw.get("name") or ""))

    # 工号：统一大写（Day 2 F-03，星火规范 ST-YYYY-NNN）
    employee_id = normalize_case(str(raw.get("employee_id") or ""), CaseMode.UPPER)

    # 部门：JSON null 加载后为 Python None，填默认部门（PRD E-02）
    department_raw = raw.get("department")
    if department_raw is None or str(department_raw).strip() == "":
        department = DEFAULT_DEPARTMENT
    else:
        department = strip_edges(str(department_raw))

    # 入职日期：Mock 中已是标准格式，仍做 strip 防御
    onboard_date = strip_edges(str(raw.get("onboard_date") or ""))

    # 手机号：删除全部空白（Day 2 F-05）
    phone = remove_all_spaces(str(raw.get("phone") or ""))

    # 住宿：保持 bool；缺失时默认 False
    need_dorm = bool(raw.get("need_dorm", False))

    # 按固定字段顺序构造，输出 JSON 键顺序稳定
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
    """
    将清洗后的列表写入 JSON 文件。

    使用 json.dump 直接写文件对象（对应讲义 load/dump 一对）。
    """
    path = Path(output_path)
    # parents=True：自动创建 output 目录
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as fp:
        json.dump(
            employees,
            fp,
            ensure_ascii=False,  # 中文部门名可读，不转 \uXXXX
            indent=2,            # 王工人工 diff 友好
        )
    return path


def print_report(
    raw_list: list[dict[str, Any]],
    cleaned_list: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """打印清洗统计报告（PRD E-05）。"""
    print("=" * 60)
    print("星火科技 · 员工 JSON 导出报告")
    print("=" * 60)
    print(f"输入条数: {len(raw_list)}")
    print(f"输出条数: {len(cleaned_list)}")
    print(f"输出文件: {output_path}")

    # 抽样展示清洗效果（验收 AC-03 对照）
    print("\n--- 清洗抽样 ---")
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
            print(f"  [{clean.get('employee_id')}] " + "; ".join(changes))

    print("\n导出完成。可用以下命令校验 JSON 格式：")
    print(f"  python3 -m json.tool {output_path}")


def main() -> None:
    """主流程：解析 → 清洗 → 导出 → 报告。"""
    raw_employees = parse_employees_from_file()
    cleaned_employees = clean_all_employees(raw_employees)
    output_path = write_employees_json(cleaned_employees)
    print_report(raw_employees, cleaned_employees, output_path)


if __name__ == "__main__":
    main()
