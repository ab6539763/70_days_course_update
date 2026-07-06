# -*- coding: utf-8 -*-
"""Day 70 验收 — SPARKTECH_MOCK=1。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
os.environ.setdefault("SPARKTECH_MOCK", "1")


def ok(m: str) -> None:
    print(f"[OK] {m}")


def fail(m: str) -> None:
    print(f"[FAIL] {m}")
    raise SystemExit(1)


def main() -> None:
    print("=== Day 70 verify ===")

    from pathlib import Path

    cap = Path(__file__).parent / "70天能力地图.md"
    if not cap.is_file() or "毕业设计" not in cap.read_text(encoding="utf-8"):
        fail("能力地图")
    ok("70天能力地图.md")

    # 轻量回归 — 仅检查关键日 verify 脚本存在
    root = Path(__file__).resolve().parents[2]
    for d in (51, 57, 58, 66):
        v = root / f"day{d}" / "code" / (f"verify_graduation.py" if d == 58 else f"verify_day{d}.py")
        if d == 58:
            v = root / "day58" / "code" / "graduation_project" / "verify_graduation.py"
        if not v.is_file():
            fail(f"missing {v}")
    ok("key verify scripts exist")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
