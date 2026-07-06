# -*- coding: utf-8 -*-
"""
Day 15 验收脚本

检查 tiktoken 演示、成本估算、客户端桥接是否正常。
无 API Key 时应在 mock 模式下全部通过。

运行：cd day15/code && python3 verify_day15.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def check_imports() -> None:
    from tiktoken_demo import count_tokens, count_messages_tokens
    from token_cost_estimator import estimate_cost, load_price_table
    from llm_compat import get_llm_client, CLIENT_SOURCE

    n, method = count_tokens("星火智服")
    if n < 1:
        fail("count_tokens 返回 0")
    ok(f"count_tokens('星火智服')={n} ({method})")

    msgs = [{"role": "user", "content": "测试"}]
    total, _ = count_messages_tokens(msgs)
    if total < 1:
        fail("count_messages_tokens 异常")
    ok(f"count_messages_tokens={total}")

    table, fx = load_price_table()
    if not table:
        fail("price_table 为空")
    ok(f"load_price_table models={len(table)} fx={fx}")


def check_estimate() -> None:
    from token_cost_estimator import estimate_cost

    scenario = (CODE_DIR / "data" / "xinghuo_proposal.txt").read_text(encoding="utf-8")
    report = estimate_cost(scenario, daily_requests=100, output_tokens=200)
    if report["input_tokens"] < 50:
        fail("input_tokens 过小")
    if not report["models"]:
        fail("models 列表为空")
    m0 = report["models"][0]
    for key in ("monthly_cost_usd", "monthly_cost_cny"):
        if key not in m0:
            fail(f"缺少字段 {key}")
    ok(f"estimate_cost input={report['input_tokens']} models={len(report['models'])}")


def check_llm_compat() -> None:
    import llm_compat
    from llm_compat import get_llm_client

    client = get_llm_client()
    resp = client.chat([{"role": "user", "content": "verify"}])
    mode = getattr(resp, "mode", getattr(client, "mode", ""))
    if mode not in ("mock", "live"):
        fail(f"未知 mode: {mode}")
    ok(f"llm_compat chat mode={mode} source={llm_compat.CLIENT_SOURCE}")


def check_scripts_run() -> None:
    for script in ("tiktoken_demo.py", "token_cost_estimator.py"):
        r = subprocess.run(
            [sys.executable, str(CODE_DIR / script), "--help"]
            if script == "token_cost_estimator.py"
            else [sys.executable, str(CODE_DIR / script), "--section", "lang"],
            capture_output=True,
            text=True,
            cwd=str(CODE_DIR),
            timeout=60,
        )
        if r.returncode != 0:
            fail(f"{script} 运行失败: {r.stderr[:200]}")
    ok("tiktoken_demo / token_cost_estimator 可执行")


def check_quiz_file() -> None:
    quiz = CODE_DIR / "model_landscape_quiz.md"
    if not quiz.is_file():
        fail("model_landscape_quiz.md 缺失")
    text = quiz.read_text(encoding="utf-8")
    if "参考答案" not in text or "Transformer" not in text:
        fail("quiz 内容不完整")
    ok("model_landscape_quiz.md 存在且含题目")


def main() -> None:
    print("=" * 60)
    print("Day 15 verify_day15.py")
    print("=" * 60)
    check_imports()
    check_estimate()
    check_llm_compat()
    check_quiz_file()
    check_scripts_run()
    print("\n✅ Day 15 全部验收通过")


if __name__ == "__main__":
    main()
