# -*- coding: utf-8 -*-
"""
星火科技 · Day 6 重构包 sparktech_export
模块：api.py
说明：Mock API 解析（自 Day 5 parse_api.py 迁移）。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CODE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MOCK_PATH = _CODE_DIR / "data" / "mock_api_response.json"
API_SUCCESS_CODE = 200


def load_mock_response(path: Path | str | None = None) -> dict[str, Any]:
    """从磁盘读取 Mock API JSON。"""
    file_path = Path(path) if path else DEFAULT_MOCK_PATH
    with file_path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def assert_api_success(root: dict[str, Any]) -> None:
    """校验业务状态码。"""
    code = root.get("code")
    if code != API_SUCCESS_CODE:
        message = root.get("message", "未知错误")
        raise ValueError(f"Mock API 业务失败: code={code}, message={message}")


def extract_employees(root: dict[str, Any]) -> list[dict[str, Any]]:
    """安全提取员工列表。"""
    data = root.get("data")
    if not isinstance(data, dict):
        return []
    employees = data.get("employees")
    if not isinstance(employees, list):
        return []
    return [item for item in employees if isinstance(item, dict)]


def get_pagination(root: dict[str, Any]) -> dict[str, int]:
    """提取分页元数据。"""
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
    """一站式解析：读文件 → 校验 → 返回 employees。"""
    root = load_mock_response(path)
    assert_api_success(root)
    return extract_employees(root)
