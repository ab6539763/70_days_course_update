# -*- coding: utf-8 -*-
"""Day 55 验收脚本 —— SPARKTECH_MOCK=1 无需 GPU / API Key。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))
os.environ.setdefault("SPARKTECH_MOCK", "1")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def main() -> None:
    print("=== Day 55 verify ===")

    from ab_test_runner import run_ab

    report = run_ab()
    if report["n"] < 1:
        fail("no golden samples")
    if report["tuned_avg"] <= report["base_avg"]:
        fail("tuned should beat base in mock")
    ok("ab_test_runner")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
