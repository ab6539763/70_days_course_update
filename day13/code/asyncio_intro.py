# -*- coding: utf-8 -*-
"""
Day 13 下午 · asyncio 入门 async/await

覆盖：
- coroutine、event loop
- await 并发 gather
- asyncio.to_thread 包装阻塞 IO（requests）
- 与 Day 13 resilient_llm_client 的衔接预览

运行：cd day13/code && python3 asyncio_intro.py
"""

from __future__ import annotations

import asyncio
import time
from typing import Any


# ---------------------------------------------------------------------------
# 第一章：最简 coroutine
# ---------------------------------------------------------------------------


async def say_after(delay: float, message: str) -> str:
    """async 函数返回 coroutine；await 让出事件循环。"""
    await asyncio.sleep(delay)
    return message


async def demo_basic() -> None:
    print("\n--- §1 async/await 基础 ---")
    start = time.perf_counter()
    result = await say_after(0.2, "星火智服")
    elapsed = time.perf_counter() - start
    print(f"结果: {result!r}, 耗时: {elapsed:.2f}s")


# ---------------------------------------------------------------------------
# 第二章：并发 gather
# ---------------------------------------------------------------------------


async def fetch_ticket(ticket_id: str) -> dict[str, Any]:
    """模拟异步拉取工单详情。"""
    await asyncio.sleep(0.15)
    return {"id": ticket_id, "status": "open", "title": f"工单 {ticket_id}"}


async def demo_gather() -> None:
    print("\n--- §2 asyncio.gather 并发 ---")
    start = time.perf_counter()
    results = await asyncio.gather(
        fetch_ticket("T-101"),
        fetch_ticket("T-102"),
        fetch_ticket("T-103"),
    )
    elapsed = time.perf_counter() - start
    print(f"并发获取 {len(results)} 条，耗时 {elapsed:.2f}s（串行约 0.45s）")
    for row in results:
        print(f"  {row}")


# ---------------------------------------------------------------------------
# 第三章：阻塞 IO 用 to_thread
# ---------------------------------------------------------------------------


def blocking_llm_mock(prompt: str) -> str:
    """模拟阻塞式 HTTP（Day 12 requests 风格）。"""
    time.sleep(0.3)
    return f"[blocking mock] {prompt[:30]}"


async def call_llm_async(prompt: str) -> str:
    """
    在 async 代码中调用阻塞函数的标准做法：
    asyncio.to_thread 把阻塞调用丢进线程池，不卡住事件循环。
    """
    return await asyncio.to_thread(blocking_llm_mock, prompt)


async def demo_to_thread() -> None:
    print("\n--- §3 asyncio.to_thread ---")
    start = time.perf_counter()
    texts = await asyncio.gather(
        call_llm_async("问题 A"),
        call_llm_async("问题 B"),
    )
    elapsed = time.perf_counter() - start
    print(f"两条阻塞调用并发完成，耗时 {elapsed:.2f}s")
    for t in texts:
        print(f"  {t}")


# ---------------------------------------------------------------------------
# 第四章：超时 wait_for
# ---------------------------------------------------------------------------


async def slow_task() -> str:
    await asyncio.sleep(2.0)
    return "完成"


async def demo_wait_for() -> None:
    print("\n--- §4 asyncio.wait_for 超时 ---")
    try:
        await asyncio.wait_for(slow_task(), timeout=0.5)
    except asyncio.TimeoutError:
        print("asyncio 层超时（与 api_decorators.timeout 互补）")


# ---------------------------------------------------------------------------
# 第五章：Task 与 create_task
# ---------------------------------------------------------------------------


async def demo_create_task() -> None:
    print("\n--- §5 create_task 后台任务 ---")
    task = asyncio.create_task(say_after(0.1, "后台完成"))
    print("主协程继续执行其他逻辑…")
    await asyncio.sleep(0.05)
    print("等待后台 task…")
    result = await task
    print(f"task 结果: {result!r}")


async def main_async() -> None:
    print("=" * 60)
    print("Day 13 下午 · asyncio_intro.py")
    print("=" * 60)
    await demo_basic()
    await demo_gather()
    await demo_to_thread()
    await demo_wait_for()
    await demo_create_task()
    print("\n✅ asyncio_intro.py 完成")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
