# -*- coding: utf-8 -*-
"""Day 52 验收脚本 —— SPARKTECH_MOCK=1 无需 GPU / API Key。"""

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
    print("=== Day 52 verify ===")

    from pathlib import Path
    from dataset_schema import validate_jsonl
    from split_dataset import build

    train, val = build()
    if not train.is_file() or not val.is_file():
        fail("jsonl not created")
    for p in (train, val):
        vr = validate_jsonl(p)
        if not vr.ok:
            fail(f"validate {p.name}: {vr.errors}")
    ok("train/val jsonl")

    if sum(1 for _ in train.open() if _.strip()) < 2:
        fail("train too small")
    ok("dataset size")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
