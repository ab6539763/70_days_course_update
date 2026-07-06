# -*- coding: utf-8 -*-
"""文件与环境配置读取。"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from sparktech.exceptions import ConfigError, DataLoadError

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]


def load_json_file(path: Path | str) -> Any:
    """读取 JSON 文件；失败时抛出 DataLoadError。"""
    file_path = Path(path)
    if not file_path.is_file():
        raise DataLoadError(f"文件不存在: {file_path}", path=str(file_path))

    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DataLoadError(f"无法读取文件: {exc}", path=str(file_path)) from exc

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise DataLoadError(
            f"JSON 解析失败（行 {exc.lineno} 列 {exc.colno}）: {exc.msg}",
            path=str(file_path),
        ) from exc


def get_env(key: str, *, default: str | None = None, required: bool = False) -> str:
    """读取环境变量；若已安装 python-dotenv 会先加载 .env。"""
    if load_dotenv is not None:
        load_dotenv()

    value = os.getenv(key, default)
    if required and not value:
        raise ConfigError(f"缺少必需环境变量: {key}", key=key)
    if value is None:
        raise ConfigError(f"环境变量未设置且无默认值: {key}", key=key)
    return value
