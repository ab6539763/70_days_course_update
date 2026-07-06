# -*- coding: utf-8 -*-
"""
Day 16 验收脚本

运行：cd day16/code && python3 verify_day16.py
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
    from llm_compat import ParametricLLMClient, get_llm_client, merge_params, load_demo_defaults

    defaults = load_demo_defaults()
    if "temperature" not in defaults:
        fail("demo_defaults 缺少 temperature")
    ok(f"load_demo_defaults temperature={defaults['temperature']}")

    merged = merge_params({"temperature": 0.5})
    if merged["temperature"] != 0.5:
        fail("merge_params 未覆盖")
    ok("merge_params 正常")


def check_chat_and_stream() -> None:
    from llm_compat import get_llm_client

    client = get_llm_client()
    messages = [
        {"role": "system", "content": "简洁回答"},
        {"role": "user", "content": "verify stream"},
    ]
    resp = client.chat(messages, temperature=0.3, max_tokens=200)
    if not resp.text:
        fail("chat 返回空")
    ok(f"chat mode={resp.mode} len={len(resp.text)}")

    chunks = list(client.chat_stream(messages, temperature=0.3))
    full = "".join(chunks)
    if not full:
        fail("stream 无输出")
    ok(f"chat_stream chunks={len(chunks)} len={len(full)}")


def check_compare_params() -> None:
    from compare_params import compare_presets

    report = compare_presets("customer_demo", ["stable", "demo_balanced"])
    if len(report["runs"]) < 2:
        fail("compare 运行数不足")
    ok(f"compare_presets runs={len(report['runs'])}")


def check_data_files() -> None:
    for name in ("demo_prompts.json", "param_presets.json"):
        p = CODE_DIR / "data" / name
        if not p.is_file():
            fail(f"缺少 {name}")
        json.loads(p.read_text(encoding="utf-8"))
    ok("data JSON 文件合法")


def check_scripts() -> None:
    scripts = [
        [sys.executable, str(CODE_DIR / "role_messages_demo.py")],
        [sys.executable, str(CODE_DIR / "stream_demo.py"), "--no-timing"],
        [sys.executable, str(CODE_DIR / "param_experiment.py"), "--param", "temperature"],
    ]
    for cmd in scripts:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(CODE_DIR), timeout=120)
        if r.returncode != 0:
            fail(f"{' '.join(cmd)} 失败: {r.stderr[:300]}")
    ok("role_messages / stream / param_experiment 可执行")


def main() -> None:
    print("=" * 60)
    print("Day 16 verify_day16.py")
    print("=" * 60)
    check_data_files()
    check_imports()
    check_chat_and_stream()
    check_compare_params()
    check_scripts()
    print("\n✅ Day 16 全部验收通过")


if __name__ == "__main__":
    main()
