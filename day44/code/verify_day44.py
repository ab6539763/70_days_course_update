# -*- coding: utf-8 -*-
"""Day 44 验收脚本 —— MCP mock 模式（无 SDK 亦可全绿）。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ["SPARKTECH_MOCK"] = "1"
os.environ.pop("OPENAI_API_KEY", None)

from agent_with_mcp import plan_tools, run_agent_with_mcp  # noqa: E402
from mcp_client_demo import run_client_demo  # noqa: E402
from mcp_compat import MCP_AVAILABLE, get_mock_server  # noqa: E402
from mock_llm import is_mock_mode  # noqa: E402
from simple_mcp_server import demo_call_tool, demo_list_tools  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_mock_llm() -> None:
    assert is_mock_mode()
    ok("mock LLM")


def test_mcp_server() -> None:
    tools = demo_list_tools()
    if len(tools) < 2:
        fail(f"工具不足: {tools}")
    kb = demo_call_tool("kb_search", {"query": "退款"})
    if "hits" not in kb and "refund" not in kb.lower():
        fail(f"kb_search 异常: {kb[:80]}")
    ticket = demo_call_tool("ticket_status", {"ticket_id": "T-1"})
    if "status" not in ticket:
        fail(f"ticket_status 异常: {ticket}")
    ok(f"mcp server tools={len(tools)} sdk={MCP_AVAILABLE}")


def test_mcp_client() -> None:
    result = run_client_demo()
    if result["kb_hits"] < 1:
        fail("client kb 无命中")
    if not result["ticket_status"]:
        fail("client ticket 无状态")
    ok("mcp client demo")


def test_mock_fallback() -> None:
    mock = get_mock_server()
    raw = mock.call_tool("kb_search", {"query": "test"})
    if not raw:
        fail("MockMCPServer 无输出")
    ok("mock MCP fallback")


def test_agent_with_mcp() -> None:
    trace = run_agent_with_mcp("工单 INC-99 和退款政策")
    if len(trace.tool_results) < 1:
        fail("agent 未调用工具")
    if not trace.answer:
        fail("agent 无回答")
    planned = plan_tools("API Key 申请流程")
    if not planned or planned[0][0] != "kb_search":
        fail(f"plan_tools 异常: {planned}")
    ok(f"agent trace tools={len(trace.tool_results)}")


def main() -> None:
    print("=== Day 44 verify ===\n")
    test_mock_llm()
    test_mcp_server()
    test_mcp_client()
    test_mock_fallback()
    test_agent_with_mcp()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
