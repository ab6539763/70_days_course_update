# -*- coding: utf-8 -*-
"""Day 17 验收脚本：python3 verify_day17.py"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from few_shot_demo import run_shot_comparison
from llm_client import LLMClient
from prompt_templates import demo_ten_prompts, load_prompt_library


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    print("=" * 60)
    print("Day 17 verify_day17.py")
    print("=" * 60)

    client = LLMClient()
    if client.mode != "mock":
        ok(f"live 模式已配置 Key，模型={client.model}")
    else:
        ok("mock 模式（无 Key）")

    library = load_prompt_library()
    if len(library) < 10:
        fail(f"prompt_library 模板不足 10 个：{len(library)}")
    ok(f"prompt_library 加载 {len(library)} 个模板")

    tasks = {t.metadata.get("task") for t in library.values()}
    for required in ("translation", "summary", "rewrite", "classification"):
        if required not in tasks:
            fail(f"缺少任务类型：{required}")
    ok("四类任务模板齐全")

    results = demo_ten_prompts()
    if len(results) != 10:
        fail(f"10 条 Prompt 实操失败：{len(results)}")
    ok("10 条 Prompt 实操通过")

    shots = run_shot_comparison()
    if len(shots) != 3:
        fail("few-shot 对比失败")
    ok("zero/one/few-shot 对比通过")

    # 分隔符与 JSON 约束冒烟
    from prompt_templates import PromptTemplate

    tpl = PromptTemplate(
        instruction="测试",
        input_text="hello",
        output_format='{"ok": true}',
    )
    prompt = tpl.build_user_prompt()
    if "<<<input>>>" not in prompt:
        fail("分隔符未注入 Prompt")
    ok("分隔符拼装正常")

    print("\n全部验收通过 ✅")


if __name__ == "__main__":
    main()
