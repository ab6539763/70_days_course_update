#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 12 · 命令行 AI 问答 v0（单轮，无历史）

星火智服里程碑：第一次从终端向 DeepSeek 提问。
Day 14 将在此基础上增加多轮对话历史。
"""

from __future__ import annotations

import argparse
import sys

from llm_client import LLMClient, LLMClientError

SYSTEM_PROMPT = (
    "你是「星火智服」智能客服助手，服务于企业内部员工。"
    "回答应简洁、准确、专业；不确定时明确说明并建议转人工。"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="星火智服 · 命令行 AI 问答 v0（单轮）",
    )
    parser.add_argument(
        "-q",
        "--question",
        help="直接提问（非交互模式）",
    )
    parser.add_argument(
        "--system",
        default=SYSTEM_PROMPT,
        help="系统提示词（默认星火智服客服人设）",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="模型名称，默认 deepseek-chat",
    )
    return parser.parse_args()


def ask_once(client: LLMClient, question: str, system_prompt: str) -> str:
    result = client.chat(question, system_message=system_prompt)
    return result.content


def interactive_loop(client: LLMClient, system_prompt: str) -> None:
    mode_hint = "MOCK（无 API Key）" if client.mock_mode else "LIVE"
    print("=" * 60)
    print("  星火智服 · 命令行 AI 问答 v0")
    print(f"  模式: {mode_hint} | 模型: {client.model}")
    print("  输入问题后回车；输入 quit / exit / q 退出")
    print("=" * 60)

    while True:
        try:
            question = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("再见！")
            break

        try:
            answer = ask_once(client, question, system_prompt)
        except LLMClientError as exc:
            print(f"[错误] {exc}")
            continue

        print(f"\n星火智服: {answer}")


def main() -> None:
    args = parse_args()
    kwargs: dict = {}
    if args.model:
        kwargs["model"] = args.model
    client = LLMClient(**kwargs)

    try:
        if args.question:
            answer = ask_once(client, args.question, args.system)
            print(answer)
        else:
            interactive_loop(client, args.system)
    except LLMClientError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
