# -*- coding: utf-8 -*-
"""
Day 15 · tiktoken 分词与 Token 计数演示

教学目标：
1. 理解 Token 与字符的区别
2. 对比中英文、混合文本的 Token 效率
3. 模拟 chat messages 的 Token 累计（教学近似）

运行：
    cd day15/code
    python3 tiktoken_demo.py
    python3 tiktoken_demo.py --section messages
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

# ---------------------------------------------------------------------------
# 分词器加载：优先 tiktoken，降级为 chars÷4
# ---------------------------------------------------------------------------

TIKTOKEN_AVAILABLE = False
try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    tiktoken = None  # type: ignore[assignment,misc]


DEFAULT_MODEL = "gpt-4o-mini"
# OpenAI chat 格式每条 message 的格式开销（教学近似，非官方精确值）
ROLE_OVERHEAD_TOKENS = 4


def get_encoding(model: str = DEFAULT_MODEL) -> Any:
    """
    获取 tiktoken 编码器。

    未安装 tiktoken 时返回 None，调用方走降级逻辑。
    """
    if not TIKTOKEN_AVAILABLE:
        return None
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        # 未知模型名时回退通用编码
        return tiktoken.get_encoding("cl100k_base")


def estimate_tokens_fallback(text: str) -> int:
    """
    降级估算：平均每 4 个字符约 1 Token（英文偏多时偏小，中文偏多时接近）。
    """
    return max(1, len(text) // 4) if text else 0


def count_tokens(text: str, *, model: str = DEFAULT_MODEL) -> tuple[int, str]:
    """
    统计文本 Token 数。

    Returns:
        (token_count, method)  — method 为 'tiktoken' 或 'fallback'
    """
    enc = get_encoding(model)
    if enc is None:
        return estimate_tokens_fallback(text), "fallback"
    return len(enc.encode(text)), "tiktoken"


def count_messages_tokens(
    messages: list[dict[str, str]], *, model: str = DEFAULT_MODEL
) -> tuple[int, str]:
    """
    累计 messages 列表 Token 数（含 role 开销近似）。

    OpenAI 官方计算更复杂；课堂用保守估算便于成本心算。
    """
    enc = get_encoding(model)
    if enc is None:
        total = sum(estimate_tokens_fallback(m.get("content", "")) for m in messages)
        total += ROLE_OVERHEAD_TOKENS * len(messages)
        return total, "fallback"

    total = sum(len(enc.encode(m.get("content", ""))) for m in messages)
    total += ROLE_OVERHEAD_TOKENS * len(messages)
    return total, "tiktoken"


def demo_compare_languages() -> None:
    """对比语义相近的中英句子 Token 效率。"""
    print("\n" + "=" * 60)
    print("【1】中英文 Token 对比")
    print("=" * 60)

    pairs = [
        ("你好，我想查询工单退款进度。", "Hello, I want to check my refund status."),
        ("星火智服智能客服系统。", "SparkTech intelligent customer service."),
        ("请用一句话解释什么是 Transformer。", "Explain Transformer in one sentence."),
    ]

    print(f"{'语言':<4} {'字符':>6} {'Token':>8} {'Token/字符':>10}  样例")
    print("-" * 60)
    for zh, en in pairs:
        for lang, text in [("中文", zh), ("英文", en)]:
            n_tok, method = count_tokens(text)
            ratio = n_tok / len(text) if text else 0
            flag = "" if method == "tiktoken" else " [fallback]"
            print(
                f"{lang:<4} {len(text):>6} {n_tok:>8} {ratio:>10.3f}  {text[:28]}{flag}"
            )


def demo_token_inspect() -> None:
    """展示 encode/decode：看前几个 Token 长什么样。"""
    print("\n" + "=" * 60)
    print("【2】Token 切分透视")
    print("=" * 60)

    sample = "星火智服 SparkTech 客服 FAQ"
    n_tok, method = count_tokens(sample)
    print(f"原文: {sample}")
    print(f"总 Token 数: {n_tok} ({method})")

    enc = get_encoding()
    if enc is None:
        print("（未安装 tiktoken，跳过逐 Token 展示）")
        return

    ids = enc.encode(sample)
    print("前 6 个 Token 片段:")
    for i, tid in enumerate(ids[:6]):
        piece = enc.decode([tid])
        print(f"  [{i}] id={tid} → {piece!r}")


def demo_messages() -> None:
    """模拟星火智服一次 API 请求的 messages 结构。"""
    print("\n" + "=" * 60)
    print("【3】messages 累计 Token（含 role 开销）")
    print("=" * 60)

    messages = [
        {
            "role": "system",
            "content": (
                "你是星火智服官方客服。基于知识库回答，不确定时引导提交工单。"
                "禁止编造退款政策。"
            ),
        },
        {"role": "user", "content": "退款一般要多久到账？"},
        {
            "role": "assistant",
            "content": "一般 3–7 个工作日，具体以支付渠道为准。",
        },
        {"role": "user", "content": "我的工单 #A8821 能加急吗？"},
    ]

    for i, m in enumerate(messages):
        n, _ = count_tokens(m["content"])
        print(f"  [{i}] {m['role']:<10} content_tokens≈{n}")

    total, method = count_messages_tokens(messages)
    print(f"\n累计（含 {ROLE_OVERHEAD_TOKENS}×{len(messages)} role 开销）: {total} tokens ({method})")
    print("提示: 还需加上预期 completion tokens 才是单次总成本。")


def demo_mixed_content() -> None:
    """长文本片段：模拟方案书节选。"""
    print("\n" + "=" * 60)
    print("【4】长文本样例")
    print("=" * 60)

    long_zh = "根据《退款管理办法》，" * 20
    n_tok, method = count_tokens(long_zh)
    print(f"重复句式 ×20 | 字符 {len(long_zh)} | Token {n_tok} ({method})")


def print_banner() -> None:
    if not TIKTOKEN_AVAILABLE:
        print(
            "⚠️  未安装 tiktoken，使用 chars÷4 降级估算。"
            "请执行: pip install tiktoken"
        )
    else:
        print(f"✓ tiktoken 已加载 | 基准模型 encoding: {DEFAULT_MODEL}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 15 tiktoken 演示")
    parser.add_argument(
        "--section",
        choices=["all", "lang", "inspect", "messages", "long"],
        default="all",
        help="运行指定章节",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Day 15 · tiktoken_demo.py")
    print("=" * 60)
    print_banner()

    sections = {
        "lang": demo_compare_languages,
        "inspect": demo_token_inspect,
        "messages": demo_messages,
        "long": demo_mixed_content,
    }

    if args.section == "all":
        demo_compare_languages()
        demo_token_inspect()
        demo_messages()
        demo_mixed_content()
    else:
        sections[args.section]()

    print("\n✅ tiktoken_demo.py 完成")


if __name__ == "__main__":
    main()
