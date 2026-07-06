# -*- coding: utf-8 -*-
"""
Day 13 上午 · 生成器与 yield

覆盖：
- yield 暂停/恢复
- 生成器表达式 vs 列表推导
- yield from 委托
- 流式读取大文件 / 模拟 LLM token 流

运行：cd day13/code && python3 generator_demo.py
"""

from __future__ import annotations

import time
from collections.abc import Generator, Iterable, Iterator
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# 第一章：基础生成器
# ---------------------------------------------------------------------------


def count_up_to(n: int) -> Generator[int, None, None]:
    """每次 yield 暂停，下次从 yield 后继续。"""
    i = 1
    while i <= n:
        print(f"  [count_up_to] 产出 {i}")
        yield i
        i += 1


def demo_basic() -> None:
    print("\n--- §1 基础 yield ---")
    gen = count_up_to(3)
    print(f"类型: {type(gen).__name__}")
    for value in gen:
        print(f"  消费 -> {value}")


# ---------------------------------------------------------------------------
# 第二章：生成器 vs 列表
# ---------------------------------------------------------------------------


def squares_list(n: int) -> list[int]:
    return [x * x for x in range(n)]


def squares_gen(n: int) -> Generator[int, None, None]:
    for x in range(n):
        yield x * x


def demo_memory() -> None:
    print("\n--- §2 惰性求值 ---")
    print(f"列表长度: {len(squares_list(5))}")
    g = squares_gen(5)
    print(f"生成器不可 len: ", end="")
    try:
        len(g)  # type: ignore[arg-type]
    except TypeError as exc:
        print(exc)


# ---------------------------------------------------------------------------
# 第三章：send / throw（进阶预览）
# ---------------------------------------------------------------------------


def echo_with_multiplier() -> Generator[int, float, str]:
    """
    双向通信生成器：
    - yield 产出值
    - send() 注入值
    - return 值通过 StopIteration.value 获取
    """
    factor = 1.0
    total = 0
    while True:
        received = yield total
        if received is None:
            continue
        factor = received
        total += int(factor)
    return "done"  # pragma: no cover


def demo_send() -> None:
    print("\n--- §3 send 注入 ---")
    gen = echo_with_multiplier()
    next(gen)  # 启动到第一个 yield
    print(f"send(2.5) -> {gen.send(2.5)}")
    print(f"send(3.0) -> {gen.send(3.0)}")


# ---------------------------------------------------------------------------
# 第四章：yield from 委托
# ---------------------------------------------------------------------------


def chain_sources(*iterables: Iterable[Any]) -> Generator[Any, None, None]:
    """将多个可迭代对象串联为一个生成器。"""
    for it in iterables:
        yield from it


def demo_yield_from() -> None:
    print("\n--- §4 yield from ---")
    merged = list(chain_sources([1, 2], ("a", "b"), range(3, 5)))
    print(f"合并结果: {merged}")


# ---------------------------------------------------------------------------
# 第五章：流式读取（LLM 场景预习）
# ---------------------------------------------------------------------------


def read_lines_lazy(path: Path) -> Generator[str, None, None]:
    """逐行读取，不一次性加载整个文件到内存。"""
    with path.open(encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")


def stream_tokens(text: str, *, chunk_size: int = 4) -> Generator[str, None, None]:
    """
    模拟 LLM streaming：按 chunk 产出 token 片段。
    Day 20 SSE 流式响应将使用类似模式。
    """
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]
        time.sleep(0.05)  # 模拟网络延迟


def demo_streaming() -> None:
    print("\n--- §5 流式 token 模拟 ---")
    reply = "星火智服工单系统支持创建、分派与闭环。"
    print("流式输出: ", end="", flush=True)
    for chunk in stream_tokens(reply, chunk_size=3):
        print(chunk, end="", flush=True)
    print()


# ---------------------------------------------------------------------------
# 第六章：生成器表达式
# ---------------------------------------------------------------------------


def demo_genexpr() -> None:
    print("\n--- §6 生成器表达式 ---")
    nums = (x * 2 for x in range(5) if x % 2 == 0)
    print(f"sum = {sum(nums)}")


def main() -> None:
    print("=" * 60)
    print("Day 13 上午 · generator_demo.py")
    print("=" * 60)
    demo_basic()
    demo_memory()
    demo_send()
    demo_yield_from()
    demo_streaming()
    demo_genexpr()
    print("\n✅ generator_demo.py 完成")


if __name__ == "__main__":
    main()
