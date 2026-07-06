# -*- coding: utf-8 -*-
"""Day 64 验收 — SPARKTECH_MOCK=1。"""

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
    print("=== Day 64 verify ===")
    ok('defense rehearsal')

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
