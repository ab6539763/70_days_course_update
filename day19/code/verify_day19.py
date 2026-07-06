# -*- coding: utf-8 -*-
"""
Day 19 验收脚本

运行：cd day19/code && python3 verify_day19.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent

SCRIPTS = [
    "tools.py",
    "tool_runner.py",
    "llm_client.py",
    "function_calling_agent.py",
]


def run_script(name: str) -> bool:
    path = CODE_DIR / name
    print(f"\n{'=' * 50}\n运行 {name}\n{'=' * 50}")
    result = subprocess.run([sys.executable, str(path)], cwd=CODE_DIR)
    ok = result.returncode == 0
    print(f"[{'OK' if ok else 'FAIL'}] {name}")
    return ok


def check_imports() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    try:
        from schemas import load_all_schemas  # noqa: F401
        from tools import get_weather, calculate, query_products  # noqa: F401
        from tool_runner import run_tool_calls  # noqa: F401
        from llm_client import ToolCallingLLMClient  # noqa: F401
        from function_calling_agent import FunctionCallingAgent  # noqa: F401
    except ImportError as exc:
        print(f"[FAIL] import: {exc}")
        return False
    print("[OK] import 全部模块")
    return True


def check_schemas() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    from schemas import load_all_schemas

    schemas = load_all_schemas()
    if len(schemas) != 3:
        print(f"[FAIL] schema 数量应为 3，实际 {len(schemas)}")
        return False
    names = {s["function"]["name"] for s in schemas}
    expected = {"get_weather", "calculate", "query_products"}
    if names != expected:
        print(f"[FAIL] schema 名称不匹配: {names}")
        return False
    print("[OK] schemas/ 三工具 schema 加载正常")
    return True


def check_tools() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    from tools import calculate, get_weather, query_products

    w = get_weather("北京")
    c = calculate("2+2")
    p = query_products("工单")
    if w.get("city") != "北京" or c.get("result") != "4" or p.get("count", 0) < 1:
        print(f"[FAIL] 工具返回值异常: {w}, {c}, {p}")
        return False
    print("[OK] 三工具执行正常")
    return True


def check_agent_mock() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    from function_calling_agent import FunctionCallingAgent

    agent = FunctionCallingAgent(verbose=False)
    if not agent.client.is_mock_mode:
        print("[SKIP] 检测到 API Key，mock agent 检查跳过")
        return True

    trace = agent.run("北京天气怎么样？")
    if not trace.final_answer:
        print(f"[FAIL] agent 无最终回答: {trace.to_dict()}")
        return False
    if len(trace.rounds) < 2:
        print(f"[FAIL] 应至少 2 轮（tool + finalize）: {len(trace.rounds)}")
        return False
    print(f"[OK] mock agent -> {trace.final_answer[:60]}…")
    return True


def main() -> int:
    print("Day 19 verify_day19.py")
    results = [
        check_imports(),
        check_schemas(),
        check_tools(),
        check_agent_mock(),
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
