# -*- coding: utf-8 -*-
"""Day 69 验收 — SPARKTECH_MOCK=1。"""

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
    print("=== Day 69 verify ===")

    from mock_interview_runner import save_report
    from pathlib import Path

    r = save_report(Path(__file__).parent / "reports" / "mock_interview.json")
    if r["average"] < 60:
        fail("score too low")
    ok("mock_interview_runner")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
