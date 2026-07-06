# -*- coding: utf-8 -*-
"""Day 52 · train/val 划分。"""

from __future__ import annotations

import json
import random
from pathlib import Path

from ticket_to_instruction import convert

DATA_DIR = Path(__file__).parent / "data"
SEED = 42


def split(records: list[dict], val_ratio: float = 0.1) -> tuple[list, list]:
    rng = random.Random(SEED)
    shuffled = records[:]
    rng.shuffle(shuffled)
    n_val = max(1, int(len(shuffled) * val_ratio))
    return shuffled[n_val:], shuffled[:n_val]


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            row = {k: r[k] for k in ("instruction", "input", "output") if k in r}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build() -> tuple[Path, Path]:
    records = convert()
    # 扩充样本以满足训练集规模演示
    templates = [
        {"instruction": "客户催促退款进度", "input": "", "output": "您好，已加急处理，1个工作日内到账。"},
        {"instruction": "客户投诉响应慢", "input": "", "output": "非常抱歉，已升级专员30分钟内回电。"},
    ]
    records.extend(templates)
    train, val = split(records)
    train_path = DATA_DIR / "train.jsonl"
    val_path = DATA_DIR / "val.jsonl"
    write_jsonl(train_path, train)
    write_jsonl(val_path, val)
    return train_path, val_path


if __name__ == "__main__":
    t, v = build()
    print(f"train={t} val={v}")
