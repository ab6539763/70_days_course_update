# -*- coding: utf-8 -*-
"""Day 40 验收脚本 —— LangChain Agent。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))
# 仅 day40/code；业务工具通过 lc_tools 内嵌路径引用 day39

os.environ["SPARKTECH_MOCK"] = "1"
os.environ.pop("OPENAI_API_KEY", None)

SCRIPTS = ["lc_tools.py", "lc_agent.py", "search_calc_agent.py"]


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def check_imports() -> bool:
    try:
        from lc_tools import get_ticket_routing_tools, classify_ticket  # noqa: F401
        from lc_agent import build_ticket_agent, run_ticket_routing  # noqa: F401
        from search_calc_agent import build_search_calc_agent  # noqa: F401
    except ImportError as exc:
        print(f"[FAIL] import: {exc}")
        return False
    ok("import 全部模块")
    return True


def check_tools_decorator() -> bool:
    from lc_tools import get_ticket_routing_tools

    tools = get_ticket_routing_tools()
    if len(tools) < 5:
        print(f"[FAIL] 工具数量不足: {len(tools)}")
        return False
    names = {t.name for t in tools}
    expected = {"classify_ticket", "route_ticket", "search_kb", "calc_priority", "calculator"}
    if names != expected:
        print(f"[FAIL] 工具名不匹配: {names}")
        return False

    out = tools[0].invoke({"text": "退款申请"})
    if "refund" not in out:
        print(f"[FAIL] classify invoke: {out}")
        return False
    ok("@tool 五工具定义与 invoke 正常")
    return True


def check_agent_executor() -> bool:
    from lc_agent import run_ticket_routing

    result = run_ticket_routing("客户要求退款，请加急处理", verbose=False)
    if not result.get("output"):
        print(f"[FAIL] agent 无 output: {result}")
        return False
    if "max iterations" in result.get("output", "").lower():
        print(f"[FAIL] agent 未正常结束: {result['output']}")
        return False
    if result.get("steps", 0) < 1:
        print(f"[FAIL] 应至少 1 步工具: {result}")
        return False
    ok(f"AgentExecutor -> {result['output'][:50]}… ({result['steps']} 步)")
    return True


def check_search_calc() -> bool:
    from search_calc_agent import demo_calc_sla

    r = demo_calc_sla()
    if not r.get("output"):
        print(f"[FAIL] search_calc 无 output")
        return False
    ok("search_calc_agent 运行正常")
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
    print("Day 40 verify_day40.py\n")
    results = [
        check_imports(),
        check_tools_decorator(),
        check_agent_executor(),
        check_search_calc(),
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
