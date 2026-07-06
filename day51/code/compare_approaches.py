# -*- coding: utf-8 -*-
"""Day 51 · RAG / Prompt / Fine-tune 场景对比。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Approach(str, Enum):
    RAG = "rag"
    FINETUNE = "finetune"
    PROMPT = "prompt"
    HYBRID = "hybrid"


@dataclass
class Scenario:
    name: str
    knowledge_updates: bool
    style_fixed: bool
    needs_citation: bool
    complexity: str  # low|medium|high


def recommend(s: Scenario) -> Approach:
  if s.needs_citation or s.knowledge_updates:
      if s.style_fixed:
          return Approach.HYBRID
      return Approach.RAG
  if s.style_fixed:
      return Approach.FINETUNE
  if s.complexity == "high":
      return Approach.PROMPT
  return Approach.PROMPT


SCENARIOS = [
    Scenario("退款政策咨询", True, False, True, "medium"),
    Scenario("标准致歉话术", False, True, False, "low"),
    Scenario("多步投诉推理", False, False, False, "high"),
    Scenario("产品规格+品牌语气", True, True, True, "medium"),
]


def main() -> None:
    print("Day 51 · compare_approaches")
    for s in SCENARIOS:
        rec = recommend(s)
        print(f"  {s.name:20s} -> {rec.value}")


if __name__ == "__main__":
    main()
