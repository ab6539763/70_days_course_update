# -*- coding: utf-8 -*-
"""Day 41 验收脚本 —— LangGraph。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ["SPARKTECH_MOCK"] = "1"
os.environ.pop("OPENAI_API_KEY", None)

SCRIPTS = ["graph_visualize.py", "langgraph_react.py", "approval_node_demo.py"]


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def check_imports() -> bool:
    try:
        from langgraph_react import build_react_graph, compile_react_agent, ReActState  # noqa: F401
        from approval_node_demo import build_approval_graph, run_demo  # noqa: F401
        from graph_visualize import export_mermaid  # noqa: F401
    except ImportError as exc:
        print(f"[FAIL] import: {exc}")
        return False
    ok("import 全部模块")
    return True


def check_react_graph() -> bool:
    from langgraph_react import run_react_graph

    result = run_react_graph("客户申请退款", verbose=False)
    if result.get("step", 0) < 1:
        print(f"[FAIL] graph 步数不足: {result}")
        return False
    if not result.get("final_answer") and not result.get("messages"):
        print(f"[FAIL] 无输出: {result}")
        return False
    ok(f"LangGraph ReAct step={result.get('step')}")
    return True


def check_approval_graph() -> bool:
    from approval_node_demo import run_demo

    out = run_demo("VIP 客户投诉退款")
    if not out.get("needs_approval"):
        print(f"[FAIL] 退款应需审批: {out}")
        return False
    if not out.get("final_message"):
        print(f"[FAIL] 无 final_message: {out}")
        return False
    ok("approval 节点 demo 正常")
    return True


def check_mermaid_export() -> bool:
    from graph_visualize import export_mermaid

    m = export_mermaid()
    if "reason" not in m or "act" not in m:
        print(f"[FAIL] mermaid 缺少节点")
        return False
    ok("Mermaid 导出正常")
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
    print("Day 41 verify_day41.py\n")
    results = [
        check_imports(),
        check_react_graph(),
        check_approval_graph(),
        check_mermaid_export(),
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
