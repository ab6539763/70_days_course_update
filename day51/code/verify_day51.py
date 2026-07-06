# -*- coding: utf-8 -*-
"""Day 51 验收脚本 —— SPARKTECH_MOCK=1 无需 GPU / API Key。"""

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
    print("=== Day 51 verify ===")

    from compare_approaches import recommend, SCENARIOS, Approach
    from finetune_decision_tree import decide

    for s in SCENARIOS:
        r = recommend(s)
        if r not in Approach:
            fail(f"invalid approach {r}")
    ok("compare_approaches")

    if decide({"style_fixed": True}) != "finetune":
        fail("decision tree style_fixed")
    ok("finetune_decision_tree")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
