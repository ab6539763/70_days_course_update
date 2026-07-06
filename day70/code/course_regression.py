# -*- coding: utf-8 -*-
"""Day 70 · 全课程回归检查（抽样）。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DAYS = [14, 36, 48, 51, 57, 58, 66]


def run_verify(day: int) -> bool:
    if day == 14:
        cmd = [sys.executable, "-m", "project1.main", "--demo-once"]
        cwd = ROOT / "day14" / "project1"
    elif day == 36:
        cmd = [sys.executable, "verify_project2.py"]
        cwd = ROOT / "day36" / "code" / "project2"
    elif day == 48:
        cmd = [sys.executable, "verify_project3.py"]
        cwd = ROOT / "day48" / "code" / "project3"
    elif day == 58:
        cmd = [sys.executable, "verify_graduation.py"]
        cwd = ROOT / "day58" / "code" / "graduation_project"
    else:
        cmd = [sys.executable, f"verify_day{day}.py"]
        cwd = ROOT / f"day{day}" / "code"
    env = {**dict(__import__("os").environ), "SPARKTECH_MOCK": "1", "PYTHONPATH": str(cwd)}
    if day == 48:
        env["PYTHONPATH"] = str(cwd)
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    return r.returncode == 0


def main() -> None:
    results = {d: run_verify(d) for d in SAMPLE_DAYS}
    for d, ok in results.items():
        print(f"day{d}: {'OK' if ok else 'FAIL'}")
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
