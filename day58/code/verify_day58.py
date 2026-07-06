# -*- coding: utf-8 -*-
"""Day 58 验收 — SPARKTECH_MOCK=1。"""

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
    print("=== Day 58 verify ===")

    import subprocess
    from pathlib import Path

    gp = Path(__file__).resolve().parent / "graduation_project"
    if not gp.is_dir():
        fail("graduation_project missing")
    ok("graduation_project dir")

    r = subprocess.run(
        [sys.executable, str(gp / "verify_graduation.py")],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        fail(r.stderr or r.stdout)
    ok("verify_graduation.py")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
