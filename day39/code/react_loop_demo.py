# -*- coding: utf-8 -*-
"""
Day 39 · ReAct 循环逐步演示

逐步打印 Thought → Action → Observation，便于课堂对照白板。

运行：cd day39/code && python3 react_loop_demo.py
"""

from __future__ import annotations

import json
import time

from react_agent import ReActAgent, parse_react_output
from tools_basic import run_tool


def demo_single_step() -> None:
    """手动演示一步解析与工具执行。"""
    sample_llm = """Thought: 这是退款类工单，需要先分类。
Action: classify_ticket
Action Input: {"text": "客户要求退款，订单已扣款"}"""

    print("=" * 60)
    print("Part 1 · 解析 LLM 输出")
    print("=" * 60)
    print(sample_llm)
    parsed = parse_react_output(sample_llm)
    print("\n解析结果:")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("Part 2 · 执行 Action → Observation")
    print("=" * 60)
    obs = run_tool(parsed["action"], parsed["action_input"])
    print(f"Action: {parsed['action']}")
    print(f"Action Input: {parsed['action_input']}")
    print(f"Observation: {obs}")


def demo_full_loop() -> None:
    """完整 Agent 循环（verbose）。"""
    print("\n" + "=" * 60)
    print("Part 3 · 完整 ReAct 循环")
    print("=" * 60)

    agent = ReActAgent(verbose=True, max_steps=5)
    query = "VIP 客户投诉退款迟迟未到账，请分类并路由"
    print(f"\n用户问题: {query}\n")

    trace = agent.run(query)
    print("\n--- 轨迹摘要 ---")
    for s in trace.steps:
        print(f"  Step {s.step}: {s.action or 'FINAL'} | thought={s.thought[:40]}…")
    print(f"  最终: {trace.final_answer}")


def demo_compare_day19() -> None:
    """对比 Day 19 Function Calling。"""
    print("\n" + "=" * 60)
    print("Part 4 · ReAct vs Day 19 Function Calling")
    print("=" * 60)
    table = """
| 维度 | Day 19 FC | Day 39 ReAct |
|------|-----------|--------------|
| 模型输出 | JSON tool_calls | 自然语言 Thought/Action |
| 解析方式 | API 结构化字段 | 正则/文本解析 |
| 可解释性 | 中 | 高（Thought 可见） |
| 稳定性 | 高 | 依赖 prompt 约束 |
| 框架 | 无 | 无（今日） |
"""
    print(table.strip())
    print("\n衔接: Day 19 schemas → Day 40 @tool → Day 41 LangGraph 图编排")


def main() -> None:
    demo_single_step()
    time.sleep(0.3)
    demo_full_loop()
    demo_compare_day19()
    print("\n✅ react_loop_demo.py 完成")


if __name__ == "__main__":
    main()
