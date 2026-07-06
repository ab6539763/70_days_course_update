# -*- coding: utf-8 -*-
"""Day 43 验收脚本 —— Supervisor 多 Agent mock 模式。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ["SPARKTECH_MOCK"] = "1"
os.environ.pop("OPENAI_API_KEY", None)

from agent_roles import RESEARCH_TEAM, run_agent  # noqa: E402
from mock_llm import is_mock_mode  # noqa: E402
from supervisor_multi_agent import compile_supervisor_app, run_research_team  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_mock_mode() -> None:
    assert is_mock_mode()
    ok("mock mode")


def test_agent_roles() -> None:
    for name in ("searcher", "analyst", "writer"):
        if name not in RESEARCH_TEAM:
            fail(f"缺少角色 {name}")
        res = run_agent(name, "测试任务")
        if not res.content:
            fail(f"{name} 无输出")
    ok("agent_roles 三角色")


def test_supervisor_pipeline() -> None:
    out = run_research_team(task="验收：多 Agent 流水线", thread_id="verify-team")
    if not out.get("search_result"):
        fail("缺少 search_result")
    if not out.get("analysis_result"):
        fail("缺少 analysis_result")
    if not out.get("report"):
        fail("缺少 report")
    if out.get("steps", 0) < 4:
        fail(f"步骤过少: {out.get('steps')}")
    if out.get("status") not in ("completed", "finished"):
        fail(f"异常 status: {out.get('status')}")
    ok(f"supervisor pipeline steps={out.get('steps')}")


def test_graph_compiled() -> None:
    app = compile_supervisor_app()
    if app is None:
        fail("graph 未编译")
    ok("supervisor graph compiled")


def main() -> None:
    print("=== Day 43 verify ===\n")
    test_mock_mode()
    test_agent_roles()
    test_supervisor_pipeline()
    test_graph_compiled()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
