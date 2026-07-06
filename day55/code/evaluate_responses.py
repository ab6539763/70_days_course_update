# -*- coding: utf-8 -*-
"""Day 55 · 简单自动评估（关键词覆盖）。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EvalScore:
    id: str
    keyword_hit: float
    length_ok: bool


def keyword_score(response: str, reference: str) -> float:
    keys = set(re.findall(r"[\u4e00-\u9fff]{2,}", reference))
    if not keys:
        return 0.0
    hit = sum(1 for k in keys if k in response)
    return hit / len(keys)


def eval_pair(item_id: str, response: str, reference: str) -> EvalScore:
    return EvalScore(item_id, keyword_score(response, reference), 20 <= len(response) <= 300)


def load_golden(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main() -> None:
    golden = load_golden(Path(__file__).parent / "data" / "golden_eval.jsonl")
    for g in golden:
        base = "您好，我们会尽快处理。"
        tuned = g["reference"] + "，感谢理解。"
        s = eval_pair(g["id"], tuned, g["reference"])
        print(g["id"], s)
