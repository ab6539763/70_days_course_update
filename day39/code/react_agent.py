# -*- coding: utf-8 -*-
"""
Day 39 · 手写 ReAct Agent（无框架）

ReAct 循环：Thought → Action → Observation → … → Final Answer

与 Day 19 Function Calling 对比：
- Day 19：模型返回结构化 tool_calls JSON
- Day 39：模型返回自然语言 ReAct 格式，需文本解析

运行：cd day39/code && python3 react_agent.py
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

from mock_llm import ReActLLMClient, build_system_prompt
from tools_basic import format_tools_prompt, run_tool


@dataclass
class ReActStep:
    """单步 ReAct 记录。"""

    step: int
    thought: str = ""
    action: str = ""
    action_input: str = ""
    observation: str = ""
    raw_llm: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
        }


@dataclass
class ReActTrace:
    """完整 ReAct 轨迹。"""

    user_query: str
    steps: list[ReActStep] = field(default_factory=list)
    final_answer: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_query": self.user_query,
            "steps": [s.to_dict() for s in self.steps],
            "final_answer": self.final_answer,
        }


# ReAct 解析正则
RE_THOUGHT = re.compile(r"Thought:\s*(.+?)(?=\n(?:Action|Final Answer)|\Z)", re.DOTALL | re.I)
RE_ACTION = re.compile(r"Action:\s*(\w+)", re.I)
RE_ACTION_INPUT = re.compile(r"Action Input:\s*(.+?)(?=\n|$)", re.DOTALL | re.I)
RE_FINAL = re.compile(r"Final Answer:\s*(.+)", re.DOTALL | re.I)


def parse_react_output(text: str) -> dict[str, str]:
    """从 LLM 文本解析 ReAct 字段。"""
    result: dict[str, str] = {"raw": text}

    thought = RE_THOUGHT.search(text)
    if thought:
        result["thought"] = thought.group(1).strip()

    final = RE_FINAL.search(text)
    if final:
        result["final_answer"] = final.group(1).strip()
        return result

    action = RE_ACTION.search(text)
    if action:
        result["action"] = action.group(1).strip()

    action_input = RE_ACTION_INPUT.search(text)
    if action_input:
        result["action_input"] = action_input.group(1).strip()

    return result


class ReActAgent:
    """
    最小 ReAct Agent。

    不依赖 LangChain / LangGraph，纯文本解析 + while 循环。
    """

    def __init__(
        self,
        llm: ReActLLMClient | None = None,
        *,
        max_steps: int = 6,
        verbose: bool = True,
    ) -> None:
        self.llm = llm or ReActLLMClient()
        self.max_steps = max_steps
        self.verbose = verbose
        self.system_prompt = build_system_prompt(format_tools_prompt())

    def run(self, user_query: str) -> ReActTrace:
        """执行 ReAct 循环直至 Final Answer 或达到 max_steps。"""
        self.llm.reset()
        trace = ReActTrace(user_query=user_query)
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query},
        ]

        for step_idx in range(1, self.max_steps + 1):
            if self.verbose:
                print(f"\n{'=' * 40}\nStep {step_idx}\n{'=' * 40}")

            response = self.llm.complete(messages)
            parsed = parse_react_output(response.text)

            step = ReActStep(
                step=step_idx,
                thought=parsed.get("thought", ""),
                raw_llm=response.text,
            )

            if self.verbose:
                print(response.text)

            # Final Answer
            if "final_answer" in parsed:
                step.thought = parsed.get("thought", step.thought)
                trace.steps.append(step)
                trace.final_answer = parsed["final_answer"]
                if self.verbose:
                    print(f"\n[Final Answer] {trace.final_answer}")
                return trace

            action = parsed.get("action", "")
            action_input = parsed.get("action_input", "")
            if not action:
                trace.steps.append(step)
                trace.final_answer = parsed.get("thought") or response.text
                if self.verbose:
                    print(f"\n[无 Action，提前结束] {trace.final_answer[:100]}")
                return trace

            observation = run_tool(action, action_input)
            step.action = action
            step.action_input = action_input
            step.observation = observation
            trace.steps.append(step)

            if self.verbose:
                print(f"\nObservation: {observation}")

            # 将 Thought+Action+Observation 追加到对话
            assistant_block = (
                f"{response.text.strip()}\n\nObservation: {observation}"
            )
            messages.append({"role": "assistant", "content": assistant_block})

        trace.final_answer = "[达到最大步数，未得到 Final Answer]"
        return trace


def main() -> None:
    queries = [
        "客户要求退款，订单已扣款，请加急处理",
        "工单 TK-20260701-001 该如何路由？",
    ]
    agent = ReActAgent(verbose=True)
    print("=" * 60)
    print(f"Day 39 · ReAct Agent（模式: {agent.llm.mode}）")
    print("=" * 60)

    for q in queries[:1]:
        print(f"\n>>> 用户: {q}")
        trace = agent.run(q)
        print(f"\n轨迹 JSON:\n{json.dumps(trace.to_dict(), ensure_ascii=False, indent=2)}")

    print("\n✅ react_agent.py 完成")


if __name__ == "__main__":
    main()
