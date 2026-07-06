# -*- coding: utf-8 -*-
"""Day 55 · Mock LLM-as-Judge。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JudgeResult:
    tone: float
    factuality: float
    overall: float


def judge(response: str, reference: str) -> JudgeResult:
    tone = 0.9 if "抱歉" in response or "您好" in response else 0.6
    fact = 0.85 if any(w in response for w in reference.split()[:2]) or reference[:2] in response else 0.5
    overall = 0.4 * tone + 0.4 * fact + 0.2 * min(1.0, len(response) / 80)
    return JudgeResult(tone, fact, round(overall, 3))


if __name__ == "__main__":
    r = judge("您好，非常抱歉，已加急处理。", "已加急，1-3工作日到账")
    print(r)
