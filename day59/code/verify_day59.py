# -*- coding: utf-8 -*-
"""Day 59 验收 — SPARKTECH_MOCK=1。"""

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
    print("=== Day 59 verify ===")

    root = CODE.parents[1]
    prd = root / "day58" / "code" / "graduation_project" / "workspace" / "demo-verify" / "docs" / "PRD.md"
    if not prd.is_file():
        import subprocess
        gp = root / "day58" / "code" / "graduation_project"
        subprocess.run(
            [sys.executable, str(gp / "scaffold.py"), "--direction", "rag_plus", "--name", "demo-verify"],
            check=False,
            cwd=str(gp),
        )
    if not prd.is_file():
        fail("PRD not found after scaffold")
    ok("PRD path ready")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
