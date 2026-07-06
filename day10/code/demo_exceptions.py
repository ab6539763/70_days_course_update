# -*- coding: utf-8 -*-
"""
Day 10 下午演示：try / except / else / finally、自定义异常、raise。

运行：cd day10/code && python3 demo_exceptions.py
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from sparktech import (  # noqa: E402
    ConfigError,
    DataLoadError,
    SparkTechError,
    ValidationError,
    get_env,
    load_json_file,
    validate_name,
    validate_phone,
)


def section(title: str) -> None:
    print(f"\n{'=' * 50}\n{title}\n{'=' * 50}")


def demo_try_except_else_finally() -> None:
    section("§1 try / except / else / finally")
    raw = '{"name": "陈晓", "phone": "13800138001"}'
    result: dict | None = None

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"解析失败: {exc}")
    else:
        print(f"else：无异常时执行，result={result}")
    finally:
        print("finally：无论成败都会执行（清理资源、关闭文件）")


def demo_raise_validation() -> None:
    section("§2 raise 自定义 ValidationError")
    cases = ["", "  ", "138", "13800138001"]
    for phone in cases:
        try:
            validate_phone(phone)
            print(f"  OK  phone={phone!r}")
        except ValidationError as exc:
            print(f"  FAIL phone={phone!r} -> [{exc.code}] {exc.message} (field={exc.field})")


def demo_catch_hierarchy() -> None:
    section("§3 按异常层次捕获")
    tasks: list[tuple[str, Callable[[], object]]] = [
        ("空姓名", lambda: validate_name("   ")),
        ("坏 JSON", lambda: load_json_file(CODE_DIR / "data" / "broken.json")),
        ("缺环境变量", lambda: get_env("SPARKTECH_API_KEY", required=True)),
    ]

    for label, fn in tasks:
        try:
            fn()
        except ValidationError as exc:
            print(f"  {label}: ValidationError -> {exc.message}")
        except DataLoadError as exc:
            print(f"  {label}: DataLoadError path={exc.path}")
        except ConfigError as exc:
            print(f"  {label}: ConfigError key={exc.key}")
        except SparkTechError as exc:
            print(f"  {label}: SparkTechError -> {exc.message}")
        else:
            print(f"  {label}: 未抛出异常")


def demo_reraise_pattern() -> None:
    section("§4 包装后 re-raise（保留链）")
    path = CODE_DIR / "data" / "missing.json"

    try:
        load_json_file(path)
    except DataLoadError:
        print(f"已记录日志: 无法加载 {path.name}")
        raise  # 调用方仍需感知失败


def main() -> None:
    print("Day 10 · demo_exceptions.py")
    demo_try_except_else_finally()
    demo_raise_validation()
    demo_catch_hierarchy()
    try:
        demo_reraise_pattern()
    except DataLoadError as exc:
        print(f"main 捕获 re-raise: {exc.message}")
    print("\n演示结束 ✓")


if __name__ == "__main__":
    main()
