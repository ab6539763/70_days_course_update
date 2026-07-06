# -*- coding: utf-8 -*-
"""
Day 16 · stream=True 流式打字机效果演示

教学目标：
1. 体验流式输出降低「首字等待」焦虑
2. 掌握 for chunk in chat_stream() 模式
3. mock 模式无外网也能彩排客户演示

运行：
    cd day16/code
    python3 stream_demo.py
    python3 stream_demo.py --question "星火智服有哪些功能？"
"""

from __future__ import annotations

import argparse
import sys
import time

from llm_compat import get_llm_client, load_demo_defaults


def typewriter_print(chunks, *, show_timing: bool = True) -> tuple[str, float | None]:
    """
    将流式 chunk 以打字机效果打印到终端。

    Args:
        chunks: 可迭代的文本片段
        show_timing: 是否打印首 chunk 延迟

    Returns:
        (完整文本, 首 chunk 毫秒延迟或 None)
    """
    start = time.perf_counter()
    first_chunk_ms: float | None = None
    parts: list[str] = []

    for chunk in chunks:
        if first_chunk_ms is None:
            first_chunk_ms = (time.perf_counter() - start) * 1000
            if show_timing:
                print(f"\n[首 chunk {first_chunk_ms:.0f} ms] ", end="")
        parts.append(chunk)
        print(chunk, end="", flush=True)

    print()  # 换行
    return "".join(parts), first_chunk_ms


def demo_stream_vs_batch() -> None:
    """对比非流式等待与流式逐字输出。"""
    client = get_llm_client()
    defaults = load_demo_defaults()

    messages = [
        {
            "role": "system",
            "content": "你是星火智服客服。回答简洁，适合现场演示朗读。",
        },
        {"role": "user", "content": "请用 4 句话介绍星火智服智能客服能力。"},
    ]
    params = {
        "temperature": defaults.get("temperature", 0.3),
        "max_tokens": defaults.get("max_tokens", 512),
        "frequency_penalty": defaults.get("frequency_penalty", 0.3),
    }

    print(f"模式: {client.mode} | 模型: {client.model}")
    print(f"参数: {params}\n")

    # 非流式
    print("── 非流式 chat() ──")
    t0 = time.perf_counter()
    batch = client.chat(messages, **params)
    batch_ms = (time.perf_counter() - t0) * 1000
    print(f"等待 {batch_ms:.0f} ms 后一次性输出:")
    print(batch.text)
    print()

    # 流式
    print("── 流式 chat_stream() ──")
    full, first_ms = typewriter_print(client.chat_stream(messages, **params))
    total_ms = batch_ms  # 近似；流式总时长在 typewriter 内
    print(f"首 chunk: {first_ms:.0f} ms | 完整长度: {len(full)} 字符")
    print("\n体验差异: 流式在首 chunk 到达后即可开始阅读。")


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 16 流式演示")
    parser.add_argument("--question", type=str, default="", help="自定义用户问题")
    parser.add_argument("--no-timing", action="store_true", help="不显示首 chunk 耗时")
    args = parser.parse_args()

    print("=" * 60)
    print("Day 16 · stream_demo.py · 流式打字机")
    print("=" * 60)

    if args.question:
        client = get_llm_client()
        messages = [
            {"role": "system", "content": "你是星火智服客服，回答简洁。"},
            {"role": "user", "content": args.question},
        ]
        print(f"问题: {args.question}\n")
        typewriter_print(
            client.chat_stream(messages, temperature=0.3),
            show_timing=not args.no_timing,
        )
    else:
        demo_stream_vs_batch()

    print("\n✅ stream_demo.py 完成")


if __name__ == "__main__":
    main()
