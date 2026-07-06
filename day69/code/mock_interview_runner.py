# -*- coding: utf-8 -*-
"""Day 69 · 三轮模拟面试记录。"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Round:
    round_id: int
    type: str  # tech | system | behavioral
    score: int
    notes: str


def run_mock() -> list[Round]:
    return [
        Round(1, "tech", 78, "RAG 召回讲清了，Agent 略弱"),
        Round(2, "system", 72, "未提 checkpointer 持久化"),
        Round(3, "behavioral", 85, "项目叙事流畅"),
    ]


def save_report(path: Path) -> dict:
    rounds = run_mock()
    avg = sum(r.score for r in rounds) / len(rounds)
    report = {"rounds": [asdict(r) for r in rounds], "average": round(avg, 1)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(save_report(Path(__file__).parent / "reports" / "mock_interview.json"))
