# -*- coding: utf-8 -*-
"""
Day 10 上午演示：import 机制、包结构、if __name__ == "__main__"。

运行：
  cd day10/code
  python3 demo_imports.py
  python3 -m demo_imports
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. 把 code/ 加入模块搜索路径（教学用；生产环境用 venv + pip install -e .）
# ---------------------------------------------------------------------------
CODE_DIR = Path(__file__).resolve().parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

# ---------------------------------------------------------------------------
# 2. 绝对导入：从包根导入公开 API
# ---------------------------------------------------------------------------
from sparktech import (  # noqa: E402
    ValidationError,
    __version__,
    normalize_phone,
    validate_name,
    validate_phone,
)
from sparktech.utils.validators import strip_field  # noqa: E402 子模块显式导入


def section(title: str) -> None:
    print(f"\n{'=' * 50}\n{title}\n{'=' * 50}")


def demo_package_api() -> None:
    section("§1 包级导入 sparktech")
    print(f"包版本: {__version__}")
    print(f"strip_field: {strip_field!r} -> {strip_field('  陈晓  ')!r}")
    print(f"normalize_phone: {normalize_phone('138 0013 8001')}")
    name = validate_name("  张工  ")
    phone = validate_phone("138-0013-8001")
    print(f"校验通过: name={name!r}, phone={phone}")


def demo_subpackage() -> None:
    section("§2 子包 sparktech.utils")
    from sparktech.utils import load_json_file

    sample = CODE_DIR / "data" / "sample_contact.json"
    payload = load_json_file(sample)
    print(f"加载 {sample.name}: keys={list(payload.keys())}")


def demo_name_main_guard() -> None:
    section("§3 if __name__ == '__main__'")
    print(f"当前模块 __name__ = {__name__!r}")
    print("直接运行本文件时 __name__ 为 '__main__'，被 import 时为模块名。")
    print("入口脚本应把可执行逻辑放在 main() 里，并用 guard 保护。")


def demo_import_styles() -> None:
    section("§4 import 三种姿势对照")
    tips = [
        "import sparktech",
        "from sparktech import validate_phone",
        "from sparktech.utils.validators import validate_phone  # 更深一层",
        "python -m demo_imports  # 以模块方式运行，便于相对路径一致",
    ]
    for line in tips:
        print(f"  · {line}")


def main() -> None:
    print("Day 10 · demo_imports.py")
    demo_package_api()
    demo_subpackage()
    demo_name_main_guard()
    demo_import_styles()
    print("\n演示结束 ✓")


if __name__ == "__main__":
    main()
