# -*- coding: utf-8 -*-
"""
星火科技 · 培训 Day 5
文件：parse_api.py
说明：读取信息科 Mock API JSON，校验业务码，提取 employees 列表。

需求追溯（PRD-SPARK-JSON-005）：
    P-01  json.load 读取 UTF-8 文件
    P-02  code == 200 校验
    P-03  返回 list[dict]
    P-04  嵌套字段安全访问

与 Day 12 衔接：
    今日 load(文件) ；日后 response.json() 得到同样结构的 dict。

作者：培训生（请修改）
日期：2026-07-10
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# 本脚本所在目录，用于定位 mock 数据文件
CODE_DIR = Path(__file__).resolve().parent
DEFAULT_MOCK_PATH = CODE_DIR / "mock_api_response.json"

# 信息科约定的成功业务码
API_SUCCESS_CODE = 200


def load_mock_response(path: Path | str | None = None) -> dict[str, Any]:
    """
    从磁盘读取 Mock API JSON 并解析为 Python dict。

    参数:
        path: JSON 文件路径，默认使用同目录下 mock_api_response.json

    返回:
        根对象 dict，包含 code、message、data 等字段

    异常:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON 格式非法
    """
    file_path = Path(path) if path else DEFAULT_MOCK_PATH
    # with 语句确保文件句柄关闭；encoding 避免中文乱码
    with file_path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def assert_api_success(root: dict[str, Any]) -> None:
    """
    校验业务状态码。非 200 时抛出 ValueError，便于上层统一处理。

    真实 HTTP 场景下还需区分 status_code（如 404）与 body 内 code。
    Day 12 会同时检查两者。
    """
    code = root.get("code")
    if code != API_SUCCESS_CODE:
        message = root.get("message", "未知错误")
        raise ValueError(f"Mock API 业务失败: code={code}, message={message}")


def extract_employees(root: dict[str, Any]) -> list[dict[str, Any]]:
    """
    从根对象中安全提取员工列表。

    使用 .get() 链式默认值，避免 data 或 employees 缺失时 KeyError。
    """
    data = root.get("data")
    if not isinstance(data, dict):
        return []
    employees = data.get("employees")
    if not isinstance(employees, list):
        return []
    # 过滤非 dict 元素，防御性编程（Mock 数据应全为 dict）
    return [item for item in employees if isinstance(item, dict)]


def get_pagination(root: dict[str, Any]) -> dict[str, int]:
    """
    提取分页元数据。作业 B3 要求实现此函数。

    返回:
        至少包含 page、total 的字典；缺失字段用 0 填充。
    """
    data = root.get("data")
    if not isinstance(data, dict):
        return {"page": 0, "total": 0}
    pagination = data.get("pagination")
    if not isinstance(pagination, dict):
        return {"page": 0, "total": 0}
    return {
        "page": int(pagination.get("page", 0) or 0),
        "total": int(pagination.get("total", 0) or 0),
    }


def parse_employees_from_file(path: Path | str | None = None) -> list[dict[str, Any]]:
    """
    一站式解析：读文件 → 校验 code → 返回 employees。

    export_employees_json.py 将 import 此函数作为数据源。
    """
    root = load_mock_response(path)
    assert_api_success(root)
    return extract_employees(root)


def main() -> None:
    """命令行入口：打印解析结果摘要，供课堂验收 AC-02。"""
    print("读取 Mock 文件:", DEFAULT_MOCK_PATH)
    root = load_mock_response()
    assert_api_success(root)

    employees = extract_employees(root)
    pagination = get_pagination(root)

    print(f"解析成功: 共 {len(employees)} 条员工记录")
    print(f"分页: page={pagination['page']}, total={pagination['total']}")

    if employees:
        first = employees[0]
        print("第一条样例:")
        print(f"  姓名: {first.get('name')!r}")
        print(f"  工号: {first.get('employee_id')!r}")
        print(f"  手机: {first.get('phone')!r}")


if __name__ == "__main__":
    main()
