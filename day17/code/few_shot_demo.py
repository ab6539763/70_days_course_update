# -*- coding: utf-8 -*-
"""
Day 17 · Zero-shot / One-shot / Few-shot 对比演示

运行：cd day17/code && python3 few_shot_demo.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from llm_client import LLMClient
from prompt_templates import PromptTemplate


@dataclass
class ShotConfig:
    name: str
    shot_type: str
    examples: list[dict[str, str]]


SENTIMENT_INPUT = "这款耳机续航不错，但佩戴有点夹耳朵。"

FEW_SHOT_EXAMPLES = [
  {
    "input": "物流超快，包装完好。",
    "output": '{"sentiment": "正面", "aspects": ["物流", "包装"]}',
  },
  {
    "input": "客服态度差，问题没解决。",
    "output": '{"sentiment": "负面", "aspects": ["客服"]}',
  },
  {
    "input": "价格一般，功能够用。",
    "output": '{"sentiment": "中性", "aspects": ["价格", "功能"]}',
  },
]


def build_sentiment_template(config: ShotConfig) -> PromptTemplate:
    return PromptTemplate(
        role="你是电商评论情感分析助手。",
        instruction="分析用户评论的情感倾向，并提取评价维度（aspects）。",
        input_text=SENTIMENT_INPUT,
        output_format='只输出 JSON：{"sentiment": "正面|负面|中性", "aspects": ["..."]}',
        examples=config.examples,
        metadata={"task": "classification", "shot_type": config.shot_type},
    )


def run_shot_comparison() -> list[dict[str, str]]:
    client = LLMClient()
    configs = [
        ShotConfig("zero-shot", "zero", []),
        ShotConfig("one-shot", "one", FEW_SHOT_EXAMPLES[:1]),
        ShotConfig("few-shot", "few", FEW_SHOT_EXAMPLES),
    ]

    rows: list[dict[str, str]] = []
    for cfg in configs:
        template = build_sentiment_template(cfg)
        response = client.chat(template.to_messages())
        rows.append(
            {
                "name": cfg.name,
                "shot_type": cfg.shot_type,
                "example_count": str(len(cfg.examples)),
                "output": response.text,
                "mode": response.mode,
            }
        )
    return rows


def demo_role_play() -> str:
    """角色扮演：资深技术文档工程师。"""
    client = LLMClient()
    template = PromptTemplate(
        role=(
            "你是星火科技资深技术文档工程师，写作风格：短句、主动语态、"
            "避免营销腔。只输出润色后的正文，不要解释。"
        ),
        instruction="将口语化描述改写为发布说明风格。",
        input_text="我们这个版本修了好多 bug，还加了个导出功能，贼好用。",
        metadata={"task": "rewrite"},
    )
    return client.chat(template.to_messages()).text


def main() -> None:
    print("=" * 60)
    print("Day 17 · few_shot_demo.py")
    print("=" * 60)

    print("\n### Zero / One / Few-shot 对比")
    for row in run_shot_comparison():
        print(f"\n[{row['name']}] examples={row['example_count']} mode={row['mode']}")
        print(row["output"])

    print("\n### 角色扮演 · 技术文档工程师")
    print(demo_role_play())

    print("\n✅ few_shot_demo.py 完成")


if __name__ == "__main__":
    main()
