# -*- coding: utf-8 -*-
"""Day 56 · 延迟 benchmark（本地函数级）。"""

from __future__ import annotations

import statistics
import time

from openai_client import local_mock_chat


def bench(n: int = 20) -> dict:
    latencies = []
    for i in range(n):
        t0 = time.perf_counter()
        local_mock_chat(f"测试退款{i}")
        latencies.append((time.perf_counter() - t0) * 1000)
    return {
        "n": n,
        "p50_ms": round(statistics.median(latencies), 2),
        "p95_ms": round(sorted(latencies)[int(n * 0.95) - 1], 2),
    }


if __name__ == "__main__":
    print(bench())
