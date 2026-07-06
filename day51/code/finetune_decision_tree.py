# -*- coding: utf-8 -*-
"""Day 51 · 可编程微调决策树。"""

from __future__ import annotations

from typing import Any


RULES: list[tuple[str, callable]] = [
    ("knowledge_updates", lambda ctx: "rag" if ctx.get("knowledge_updates") else None),
    ("needs_citation", lambda ctx: "rag" if ctx.get("needs_citation") else None),
    ("style_fixed", lambda ctx: "finetune" if ctx.get("style_fixed") else None),
    ("high_complexity", lambda ctx: "prompt" if ctx.get("complexity") == "high" else None),
    ("hybrid_brand_rag", lambda ctx: "hybrid" if ctx.get("style_fixed") and ctx.get("knowledge_updates") else None),
]


def decide(ctx: dict[str, Any]) -> str:
    for name, fn in RULES:
        result = fn(ctx)
        if result:
            return result
    return "prompt"


def main() -> None:
    tests = [
        {"name": "政策+引用", "knowledge_updates": True, "needs_citation": True},
        {"name": "致歉模板", "style_fixed": True},
        {"name": "复杂推理", "complexity": "high"},
    ]
    for t in tests:
        label = t.pop("name")
        print(f"  {label}: {decide(t)}")


if __name__ == "__main__":
    main()
