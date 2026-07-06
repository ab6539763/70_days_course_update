# -*- coding: utf-8 -*-
"""毕业设计骨架验收。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def ok(m: str) -> None:
    print(f"[OK] {m}")


def fail(m: str) -> None:
    print(f"[FAIL] {m}")
    raise SystemExit(1)


def main() -> None:
    print("=== Graduation skeleton verify ===")
    for d in ("directions", "templates"):
        if not (ROOT / d).is_dir() and d == "directions":
            pass
    directions = list((ROOT / "directions").glob("*.md"))
    if len(directions) < 8:
        fail(f"directions count {len(directions)}")
    ok("8 directions")

    demo = ROOT / "workspace" / "demo-verify"
    r = subprocess.run(
        [sys.executable, str(ROOT / "scaffold.py"), "--direction", "rag_plus", "--name", "demo-verify"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        fail(f"scaffold: {r.stderr}")
    ok("scaffold.py")

    if not (demo / "project_meta.json").is_file():
        fail("project_meta missing")
    ok("workspace demo")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
