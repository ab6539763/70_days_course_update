# -*- coding: utf-8 -*-
"""Day 39 验收脚本 —— 手写 ReAct Agent。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
os.environ["SPARKTECH_MOCK"] = "1"
os.environ.pop("OPENAI_API_KEY", None)
sys.path.insert(0, str(CODE_DIR))

SCRIPTS = ["tools_basic.py", "react_loop_demo.py", "react_agent.py"]


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> int:
    print(f"[FAIL] {msg}")
    return 1


def check_imports() -> bool:
    try:
        from tools_basic import TOOL_REGISTRY, classify_ticket, run_tool  # noqa: F401
        from mock_llm import ReActLLMClient, is_mock_mode  # noqa: F401
        from react_agent import ReActAgent, parse_react_output  # noqa: F401
    except ImportError as exc:
        print(f"[FAIL] import: {exc}")
        return False
    ok("import 全部模块")
    return True


def check_tools() -> bool:
    from tools_basic import classify_ticket, route_ticket, search_kb_snippet

    c = classify_ticket("客户要求退款，订单扣款")
    if c.get("intent") != "refund":
        print(f"[FAIL] classify 应为 refund: {c}")
        return False

    r = route_ticket("refund", "vip")
    if r.get("team") != "billing":
        print(f"[FAIL] route 应为 billing: {r}")
        return False

    kb = search_kb_snippet("退款")
    if kb.get("count", 0) < 1:
        print(f"[FAIL] kb 检索为空: {kb}")
        return False

    ok("工单工具 classify/route/kb 正常")
    return True


def check_parse_react() -> bool:
    from react_agent import parse_react_output

    text = (
        "Thought: 需要分类\n"
        "Action: classify_ticket\n"
        'Action Input: {"text": "退款"}'
    )
    parsed = parse_react_output(text)
    if parsed.get("action") != "classify_ticket":
        print(f"[FAIL] 解析 action 失败: {parsed}")
        return False

    final_text = "Thought: 完成\nFinal Answer: 已路由到账单组"
    final = parse_react_output(final_text)
    if "已路由" not in final.get("final_answer", ""):
        print(f"[FAIL] 解析 Final Answer 失败: {final}")
        return False

    ok("ReAct 文本解析正常")
    return True


def check_react_agent() -> bool:
    from react_agent import ReActAgent

    agent = ReActAgent(verbose=False, max_steps=5)
    trace = agent.run("客户要求退款，请加急")
    if not trace.final_answer:
        print(f"[FAIL] 无 final_answer: {trace.to_dict()}")
        return False
    if len(trace.steps) < 1:
        print(f"[FAIL] 应至少 1 步: {len(trace.steps)}")
        return False
    actions = [s.action for s in trace.steps if s.action]
    if not actions:
        print(f"[FAIL] 应有至少一个 Action: {trace.to_dict()}")
        return False
    ok(f"ReAct agent -> {trace.final_answer[:50]}… ({len(trace.steps)} 步)")
    return True


def run_script(name: str) -> bool:
    path = CODE_DIR / name
    print(f"\n--- 运行 {name} ---")
    result = subprocess.run([sys.executable, str(path)], cwd=CODE_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        print(f"[FAIL] {name}")
        return False
    print(f"[OK] {name}")
    return True


def main() -> int:
    print("Day 39 verify_day39.py\n")
    results = [
        check_imports(),
        check_tools(),
        check_parse_react(),
        check_react_agent(),
        *[run_script(s) for s in SCRIPTS],
    ]
    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 50}")
    print(f"验收结果: {passed}/{total} 通过")
    print("=" * 50)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
