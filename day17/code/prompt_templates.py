# -*- coding: utf-8 -*-
"""
Day 17 · Prompt 模板引擎

实现 Instruction / Context / Input / Output 四要素拼装，
支持分隔符、角色扮演、JSON 输出约束。

运行：cd day17/code && python3 prompt_templates.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from llm_client import LLMClient


DEFAULT_DELIMITER_START = "<<<"
DEFAULT_DELIMITER_END = ">>>"


@dataclass
class PromptTemplate:
    """
    Prompt 四要素模板。

    - instruction: 任务指令（做什么）
    - context: 背景知识 / 参考文档（可选）
    - input_text: 待处理用户输入
    - output_format: 输出格式约束（如 JSON schema 描述）
    - role: 角色扮演（system 人设）
    """

    instruction: str
    input_text: str = ""
    context: str = ""
    output_format: str = ""
    role: str = "你是星火科技企业内部 AI 助手，回答简洁、专业。"
    delimiter_start: str = DEFAULT_DELIMITER_START
    delimiter_end: str = DEFAULT_DELIMITER_END
    examples: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def wrap_input(self, text: str | None = None) -> str:
        body = text if text is not None else self.input_text
        return f"{self.delimiter_start}input{self.delimiter_end}\n{body}\n{self.delimiter_start}/input{self.delimiter_end}"

    def build_user_prompt(self) -> str:
        sections: list[str] = [f"## 指令\n{self.instruction.strip()}"]

        if self.context.strip():
            sections.append(
                f"## 上下文\n{self.delimiter_start}context{self.delimiter_end}\n"
                f"{self.context.strip()}\n"
                f"{self.delimiter_start}/context{self.delimiter_end}"
            )

        if self.examples:
            lines = ["## 示例"]
            for idx, ex in enumerate(self.examples, start=1):
                lines.append(f"示例 {idx} 输入：{ex.get('input', '')}")
                lines.append(f"示例 {idx} 输出：{ex.get('output', '')}")
            sections.append("\n".join(lines))

        sections.append(f"## 待处理\n{self.wrap_input()}")

        if self.output_format.strip():
            sections.append(f"## 输出格式\n{self.output_format.strip()}")

        sections.append("请严格按输出格式回复，不要输出与任务无关的内容。")
        return "\n\n".join(sections)

    def to_messages(self) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.role},
            {"role": "user", "content": self.build_user_prompt()},
        ]


def load_prompt_library(library_dir: Path | None = None) -> dict[str, PromptTemplate]:
    """从 prompt_library/*.json 加载预置模板。"""
    base = library_dir or Path(__file__).resolve().parent / "prompt_library"
    templates: dict[str, PromptTemplate] = {}
    if not base.is_dir():
        return templates

    for path in sorted(base.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        templates[path.stem] = PromptTemplate(**data)
    return templates


def run_template(client: LLMClient, template: PromptTemplate, label: str) -> dict[str, Any]:
    messages = template.to_messages()
    response = client.chat(messages)
    return {
        "label": label,
        "task": template.metadata.get("task", "general"),
        "mode": response.mode,
        "output": response.text,
        "latency_ms": response.latency_ms,
    }


def demo_ten_prompts() -> list[dict[str, Any]]:
    """课堂实操：10 条 Prompt（翻译/摘要/改写/分类）。"""
    client = LLMClient()
    library = load_prompt_library()
    if len(library) < 10:
        raise RuntimeError(f"prompt_library 应至少 10 个模板，当前 {len(library)}")

    results: list[dict[str, Any]] = []
    for name in sorted(library.keys())[:10]:
        results.append(run_template(client, library[name], label=name))
    return results


def main() -> None:
    print("=" * 60)
    print("Day 17 · prompt_templates.py · 10 条 Prompt 实操")
    print("=" * 60)

    client = LLMClient()
    print(f"LLM 模式: {client.mode}\n")

    for item in demo_ten_prompts():
        print(f"[{item['label']}] task={item['task']} ({item['latency_ms']} ms)")
        print(item["output"])
        print("-" * 40)

    print("\n✅ prompt_templates.py 完成")


if __name__ == "__main__":
    main()
