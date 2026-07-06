# -*- coding: utf-8 -*-
"""Day 19 · OpenAI 兼容 tools schema 加载器。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_DIR = Path(__file__).resolve().parent

SCHEMA_FILES = {
    "get_weather": "weather.json",
    "calculate": "calculator.json",
    "query_products": "db_query.json",
}


def load_schema(name: str) -> dict[str, Any]:
    """按工具名加载单个 JSON schema。"""
    filename = SCHEMA_FILES.get(name)
    if not filename:
        raise KeyError(f"未知 schema: {name}")
    path = SCHEMA_DIR / filename
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_all_schemas() -> list[dict[str, Any]]:
    """加载全部工具 schema，供 chat/completions 的 tools 参数使用。"""
    return [load_schema(name) for name in SCHEMA_FILES]


def schema_names() -> list[str]:
    return list(SCHEMA_FILES.keys())
