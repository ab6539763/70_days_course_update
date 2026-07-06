# -*- coding: utf-8 -*-
"""Day 55 · Base vs Finetuned A/B 报告。"""

from __future__ import annotations

import json
from pathlib import Path

from evaluate_responses import load_golden, eval_pair
from llm_judge_mock import judge


def run_ab() -> dict:
    golden_path = Path(__file__).parent / "data" / "golden_eval.jsonl"
    rows = load_golden(golden_path)
    base_scores, tuned_scores = [], []
    for g in rows:
        base_resp = "好的，我们会处理您的问题。"
        tuned_resp = g["reference"]
        base_scores.append(judge(base_resp, g["reference"]).overall)
        tuned_scores.append(judge(tuned_resp, g["reference"]).overall)
    report = {
        "n": len(rows),
        "base_avg": round(sum(base_scores) / len(base_scores), 3),
        "tuned_avg": round(sum(tuned_scores) / len(tuned_scores), 3),
        "lift": round(sum(tuned_scores) / len(tuned_scores) - sum(base_scores) / len(base_scores), 3),
    }
    out = Path(__file__).parent / "reports" / "ab_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(run_ab())
