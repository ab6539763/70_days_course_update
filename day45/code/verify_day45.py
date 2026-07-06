# -*- coding: utf-8 -*-
"""Day 45 验收脚本 —— 无 API Key 时全部 mock 通过。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
ROOT = CODE_DIR.parent
sys.path.insert(0, str(CODE_DIR))

os.environ.setdefault("SPARKTECH_MOCK", "1")

from integrated_agent_review import (  # noqa: E402
    ConversationSession,
    IntegratedAgentReview,
    ToolRegistry,
)
from mock_llm import build_agent_llm, is_mock_mode  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_mock_mode() -> None:
    assert is_mock_mode()
    ok("mock mode enabled")


def test_quiz_file() -> None:
    quiz = ROOT / "code" / "week5_review_quiz.md"
    if not quiz.is_file():
        fail("week5_review_quiz.md 缺失")
    text = quiz.read_text(encoding="utf-8")
    if "ReAct" not in text and "Agent" not in text:
        fail("测验题应包含 Agent 相关内容")
    ok("week5_review_quiz.md exists")


def test_dify_notes() -> None:
    notes = ROOT / "code" / "dify_workflow_notes.md"
    if not notes.is_file():
        fail("dify_workflow_notes.md 缺失")
    text = notes.read_text(encoding="utf-8")
    for keyword in ("Dify", "Coze", "工作流"):
        if keyword not in text:
            fail(f"dify_workflow_notes 应包含 {keyword}")
    ok("dify_workflow_notes.md exists")


def test_session() -> None:
    s = ConversationSession()
    s.add_user("你好")
    s.add_assistant("你好！")
    assert s.message_count >= 3
    s.clear()
    assert s.message_count == 1
    ok("ConversationSession")


def test_tools() -> None:
    reg = ToolRegistry()
    names = reg.list_tools()
    for required in ("get_weather", "lookup_order", "calc", "search_knowledge"):
        if required not in names:
            fail(f"缺少工具 {required}")
    w = reg.execute("get_weather", {"city": "北京"})
    assert "北京" in w
    k = reg.execute("search_knowledge", {"query": "退款"})
    assert "退款" in k
    ok("ToolRegistry four tools")


def test_agent_rounds() -> None:
    agent = IntegratedAgentReview()
    t1 = agent.run("北京天气怎么样")
    assert t1.final_answer
    assert any(r.get("tool_calls") for r in t1.rounds) or "北京" in t1.final_answer

    agent2 = IntegratedAgentReview()
    t2 = agent2.run("知识库查退款政策")
    assert t2.final_answer

    agent3 = IntegratedAgentReview()
    t3 = agent3.run("计算 3+4")
    assert "7" in t3.final_answer or any(
        "7" in str(tc.get("result", ""))
        for r in t3.rounds
        for tc in r.get("tool_calls", [])
    )
    ok("IntegratedAgentReview weather/kb/calc")


def test_mock_llm() -> None:
    llm = build_agent_llm()
    result = llm.chat(
        [{"role": "user", "content": "上海天气"}],
        [{"type": "function", "function": {"name": "get_weather"}}],
    )
    assert result.tool_calls or result.content
    ok("MockAgentLLM")


def main() -> None:
    print("=== Day 45 verify ===\n")
    test_mock_mode()
    test_quiz_file()
    test_dify_notes()
    test_session()
    test_tools()
    test_mock_llm()
    test_agent_rounds()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
