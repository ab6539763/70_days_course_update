# -*- coding: utf-8 -*-
"""
Day 18 · Chain-of-Thought（思维链）演示

对比：直接作答 vs 要求逐步思考（CoT）。
扩展概念：Self-Consistency、Tree-of-Thoughts（概念讲解 + 模拟）。

运行：cd day18/code && python3 cot_demo.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from llm_client import LLMClient


MATH_PROBLEM = "一家门店周一卖 12 件、周二卖 18 件、周三卖 15 件，三天平均销量是多少？"


@dataclass
class CotVariant:
    name: str
    use_cot: bool
    temperature: float


def build_messages(problem: str, use_cot: bool) -> list[dict[str, str]]:
    if use_cot:
        user = (
            "请逐步思考（Chain of Thought）再给出最终答案。\n"
            f"<problem>{problem}</problem>\n"
            "输出结构：\n思考过程：...\n最终答案：..."
        )
    else:
        user = f"直接给出答案，不要解释步骤。\n<problem>{problem}</problem>"
    return [
        {"role": "system", "content": "你是小学数学助教。"},
        {"role": "user", "content": user},
    ]


def run_cot_comparison(client: LLMClient) -> list[dict[str, str]]:
    variants = [
        CotVariant("direct", use_cot=False, temperature=0.0),
        CotVariant("chain-of-thought", use_cot=True, temperature=0.2),
    ]
    rows: list[dict[str, str]] = []
    for v in variants:
        resp = client.chat(
            build_messages(MATH_PROBLEM, v.use_cot),
            temperature=v.temperature,
        )
        rows.append({"variant": v.name, "output": resp.text, "mode": resp.mode})
    return rows


def demo_self_consistency() -> dict[str, object]:
    """
    Self-Consistency 概念演示（mock 多路径投票）。

    真实场景：同一 CoT Prompt 采样 N 次，对最终答案多数投票。
    此处用确定性 mock 模拟 3 条推理链与投票结果。
    """
    chains = [
        "12+18+15=45，45/3=15",
        "总和 45，三天，均值 15",
        "平均 = (12+18+15)/3 = 15",
    ]
    votes = {"15": 3}
    return {
        "technique": "self-consistency",
        "sample_count": 3,
        "chains": chains,
        "vote_result": votes,
        "final_answer": max(votes, key=votes.get),
    }


def demo_tree_of_thoughts() -> dict[str, object]:
    """
    Tree of Thoughts 概念演示（不调用真实搜索，仅展示分支结构）。

    场景：客服话术生成——先发散多种策略，再评估选优。
    """
    return {
        "technique": "tree-of-thoughts",
        "root": "用户投诉物流延迟",
        "branches": [
            {"path": "道歉 + 补偿券", "score": 0.82},
            {"path": "解释天气原因", "score": 0.45},
            {"path": "转人工专员", "score": 0.91},
        ],
        "selected": "转人工专员",
    }


def main() -> None:
    print("=" * 60)
    print("Day 18 · cot_demo.py")
    print("=" * 60)

    client = LLMClient()
    print(f"模式: {client.mode}\n")

    print("### Direct vs CoT")
    for row in run_cot_comparison(client):
        print(f"\n--- {row['variant']} ({row['mode']}) ---")
        print(row["output"])

    print("\n### Self-Consistency（概念模拟）")
    print(json.dumps(demo_self_consistency(), ensure_ascii=False, indent=2))

    print("\n### Tree of Thoughts（概念模拟）")
    print(json.dumps(demo_tree_of_thoughts(), ensure_ascii=False, indent=2))

    print("\n✅ cot_demo.py 完成")


if __name__ == "__main__":
    main()
