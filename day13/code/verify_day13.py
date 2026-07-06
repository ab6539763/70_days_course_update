# -*- coding: utf-8 -*-
"""
Day 13 验收脚本：一键跑通全部演示 + 弹性客户端 mock 路径。

运行：cd day13/code && python3 verify_day13.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent

SCRIPTS = [
    "decorator_demo.py",
    "generator_demo.py",
    "typing_demo.py",
    "asyncio_intro.py",
    "api_decorators.py",
    "llm_client.py",
    "resilient_llm_client.py",
]


def run_script(name: str) -> bool:
    path = CODE_DIR / name
    print(f"\n{'=' * 50}\n运行 {name}\n{'=' * 50}")
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=CODE_DIR,
        capture_output=False,
    )
    ok = result.returncode == 0
    print(f"[{'OK' if ok else 'FAIL'}] {name}")
    return ok


def check_imports() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    try:
        from api_decorators import retry, timeout  # noqa: F401
        from llm_client import LLMClient  # noqa: F401
        from resilient_llm_client import ResilientLLMClient  # noqa: F401
    except ImportError as exc:
        print(f"[FAIL] import 检查: {exc}")
        return False
    print("[OK] import api_decorators / llm_client / resilient_llm_client")
    return True


def check_mock_chat() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    from resilient_llm_client import ResilientLLMClient

    client = ResilientLLMClient()
    if not client.is_mock_mode:
        print("[SKIP] 检测到 OPENAI_API_KEY，mock 检查跳过")
        return True
    result = client.chat([{"role": "user", "content": "验收"}])
    if result.mode != "mock" or not result.text:
        print(f"[FAIL] mock chat: {result}")
        return False
    print(f"[OK] mock chat -> {result.text[:50]}…")
    return True


def main() -> int:
    print("Day 13 verify_day13.py")
    results: list[bool] = [check_imports(), check_mock_chat()]
    results.extend(run_script(s) for s in SCRIPTS)

    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 50}")
    print(f"验收结果: {passed}/{total} 通过")
    print("=" * 50)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
