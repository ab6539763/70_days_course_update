# -*- coding: utf-8 -*-
"""Day 56 验收脚本 —— SPARKTECH_MOCK=1 无需 GPU / API Key。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))
os.environ.setdefault("SPARKTECH_MOCK", "1")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def main() -> None:
    print("=== Day 56 verify ===")

    from mock_vllm_server import generate_reply, ChatMessage
    from openai_client import local_mock_chat
    from benchmark_latency import bench

    r = generate_reply([ChatMessage(role="user", content="退款怎么办")])
    if "退款" not in r:
        fail("mock reply missing keyword")
    ok("mock_vllm_server")

    r2 = local_mock_chat("投诉太慢")
    if "抱歉" not in r2:
        fail("local mock complaint")
    ok("openai_client")

    stats = bench(n=10)
    if stats["p95_ms"] > 5000:
        fail("latency too high")
    ok("benchmark_latency")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
