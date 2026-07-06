# -*- coding: utf-8 -*-
"""
Day 10 包结构验收脚本。
运行：cd day10/code && python3 verify_package.py
"""

from __future__ import annotations

import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))


def check_imports() -> None:
    from sparktech import __version__, normalize_phone, validate_name, validate_phone

    assert __version__ == "0.1.0"
    assert validate_name("  李雷  ") == "李雷"
    assert validate_phone("138 0013 8001") == "13800138001"
    assert normalize_phone("138-0013-8001") == "13800138001"
    print("[OK] sparktech 公开 API")


def check_exceptions() -> None:
    from sparktech import DataLoadError, ValidationError, load_json_file, validate_name

    try:
        validate_name("")
    except ValidationError as exc:
        assert exc.field == "name"
        assert exc.code == "VALIDATION_ERROR"
    else:
        raise AssertionError("应抛出 ValidationError")

    broken = CODE_DIR / "data" / "broken.json"
    try:
        load_json_file(broken)
    except DataLoadError as exc:
        assert exc.path.endswith("broken.json")
    else:
        raise AssertionError("应抛出 DataLoadError")

    print("[OK] 自定义异常与 raise")


def check_json_load() -> None:
    from sparktech import load_json_file

    sample = CODE_DIR / "data" / "sample_contact.json"
    data = load_json_file(sample)
    assert data["name"] == "陈晓"
    assert data["phone"] == "13800138001"
    print("[OK] utils.io.load_json_file")


def check_utils_subpackage() -> None:
    from sparktech.utils.validators import strip_field

    assert strip_field("  ok  ") == "ok"
    print("[OK] sparktech.utils 子包")


def main() -> None:
    print("Day 10 包结构验收")
    print("-" * 40)
    check_imports()
    check_exceptions()
    check_json_load()
    check_utils_subpackage()
    print("-" * 40)
    print("全部通过 ✓")


if __name__ == "__main__":
    main()
