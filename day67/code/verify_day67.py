# -*- coding: utf-8 -*-
"""Day 67 验收 — SPARKTECH_MOCK=1。"""

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
    print("=== Day 67 verify ===")

    from code_interview_drills import top_k_similar
    from pathlib import Path

    idx = top_k_similar([1.0, 0.0], [[1.0, 0.0], [0.0, 1.0]], k=1)
    if idx != [0]:
        fail("top_k")
    ok("code_interview_drills")

    md = Path(__file__).parent / "interview_llm_100.md"
    if not md.is_file() or "RAG" not in md.read_text(encoding="utf-8"):
        fail("interview index")
    ok("interview_llm_100.md")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
