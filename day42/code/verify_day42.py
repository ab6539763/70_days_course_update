# -*- coding: utf-8 -*-
"""Day 42 验收脚本 —— LangGraph 进阶 mock 模式。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ["SPARKTECH_MOCK"] = "1"
os.environ.pop("OPENAI_API_KEY", None)

from checkpointer_demo import compare_threads, run_demo  # noqa: E402
from human_in_loop import compile_review_app, run_hitl_flow  # noqa: E402
from mock_llm import build_chat_model, is_mock_mode  # noqa: E402
from writing_agent_graph import compile_writing_app, run_writing_agent  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_mock_llm() -> None:
    assert is_mock_mode()
    llm = build_chat_model()
    text = llm.invoke("test").content
    if not text:
        fail("mock llm 无输出")
    ok("mock LLM")


def test_checkpointer() -> None:
    log = run_demo(thread_id="verify-cp")
    counts = [r["count"] for r in log["invocations"]]
    if counts != [1, 2, 3]:
        fail(f"checkpointer 未累加: {counts}")
    isolated = compare_threads()
    if isolated["thread_a"]["count"] != 2:
        fail(f"thread-a 应为 2: {isolated['thread_a']}")
    if isolated["thread_b"]["count"] != 1:
        fail(f"thread-b 应为 1: {isolated['thread_b']}")
    ok(f"checkpointer 累加 {counts}")


def test_human_in_loop() -> None:
    result = run_hitl_flow(topic="验收测试", human_decision="approve", thread_id="verify-hitl")
    if not result["paused_state"].get("draft"):
        fail("interrupt 前应有 draft")
    if "review" not in result["pending_nodes"]:
        fail(f"应在 review 暂停: {result['pending_nodes']}")
    if not result["final_state"].get("approved"):
        fail("resume approve 后应 approved")
    app = compile_review_app()
    assert app is not None
    ok("human-in-the-loop interrupt/resume")


def test_writing_graph() -> None:
    out = run_writing_agent(topic="验收写作", thread_id="verify-write")
    notes = out.get("research_notes", [])
    if len(notes) < 2:
        fail(f"并行节点应产出 >=2 条笔记: {notes}")
    if not out.get("draft"):
        fail("应有 draft")
    if out.get("retry_count", 0) < 1:
        fail("应触发至少一次重试")
    if out.get("status") not in ("已发布", "降级发布"):
        fail(f"异常 status: {out.get('status')}")
    app = compile_writing_app()
    assert app is not None
    ok(f"writing graph notes={len(notes)} retries={out.get('retry_count')}")


def main() -> None:
    print("=== Day 42 verify ===\n")
    test_mock_llm()
    test_checkpointer()
    test_human_in_loop()
    test_writing_graph()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
