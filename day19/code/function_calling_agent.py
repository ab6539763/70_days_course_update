# -*- coding: utf-8 -*-
"""
Day 19 · 手写 Function Calling Agent（无框架，纯 API）

流程：
1. 将 tools schema 随用户消息发给模型
2. 若模型返回 tool_calls → tool_runner 执行 → 结果作为 tool 消息回传
3. 循环直至模型返回纯文本或达到 max_rounds

运行：cd day19/code && python3 function_calling_agent.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any

from llm_client import ChatCompletionResult, ToolCallingLLMClient
from schemas import load_all_schemas
from tool_runner import run_tool_calls


@dataclass
class AgentTrace:
    """一次对话的完整轨迹，便于调试与教学。"""

    user_query: str
    rounds: list[dict[str, Any]] = field(default_factory=list)
    final_answer: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_query": self.user_query,
            "rounds": self.rounds,
            "final_answer": self.final_answer,
        }


class FunctionCallingAgent:
    """
    最小可用 Function Calling Agent。

    不依赖 LangChain / OpenAI SDK，仅用 requests + 手写循环。
    """

    def __init__(
        self,
        client: ToolCallingLLMClient | None = None,
        *,
        max_rounds: int = 5,
        verbose: bool = True,
    ) -> None:
        self.client = client or ToolCallingLLMClient()
        self.tools = load_all_schemas()
        self.max_rounds = max_rounds
        self.verbose = verbose

    def run(self, user_query: str) -> AgentTrace:
        """执行一轮用户问答，自动处理多轮 tool calling。"""
        trace = AgentTrace(user_query=user_query)
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "你是星火智服 AI 助手。需要实时数据或计算时，请调用提供的工具；"
                    "拿到工具结果后，用简洁中文回答用户。"
                ),
            },
            {"role": "user", "content": user_query},
        ]

        for round_idx in range(1, self.max_rounds + 1):
            if self.verbose:
                print(f"\n--- Round {round_idx} ---")

            result = self.client.chat_with_tools(messages, self.tools)
            round_log = self._log_round(round_idx, result)
            trace.rounds.append(round_log)

            assistant_msg = self._build_assistant_message(result)
            messages.append(assistant_msg)

            if not result.message.has_tool_calls:
                trace.final_answer = result.message.content or ""
                if self.verbose:
                    print(f"\n[最终回答] {trace.final_answer}")
                return trace

            if self.verbose:
                for tc in result.message.tool_calls:
                    fn = tc.get("function", {})
                    print(f"  → tool_call: {fn.get('name')}({fn.get('arguments')})")

            report = run_tool_calls(result.message.tool_calls)
            messages.extend(report.tool_messages)

            if self.verbose:
                for r in report.results:
                    status = "OK" if r.success else "FAIL"
                    print(f"  ← [{status}] {r.name}: {json.dumps(r.output, ensure_ascii=False)[:120]}")

            round_log["tool_results"] = [
                {"name": r.name, "success": r.success, "output": r.output, "error": r.error}
                for r in report.results
            ]

        trace.final_answer = "[agent] 超过最大 tool 轮次，请简化问题。"
        return trace

    def _build_assistant_message(self, result: ChatCompletionResult) -> dict[str, Any]:
        msg: dict[str, Any] = {
            "role": "assistant",
            "content": result.message.content,
        }
        if result.message.has_tool_calls:
            msg["tool_calls"] = result.message.tool_calls
        return msg

    def _log_round(self, round_idx: int, result: ChatCompletionResult) -> dict[str, Any]:
        return {
            "round": round_idx,
            "mode": result.mode,
            "finish_reason": result.finish_reason,
            "latency_ms": result.latency_ms,
            "has_tool_calls": result.message.has_tool_calls,
            "content_preview": (result.message.content or "")[:100],
        }


DEMO_QUERIES = [
    "北京今天天气怎么样？",
    "帮我算一下 (12 + 8) * 3 等于多少",
    "查一下工单相关的产品",
    "上海天气如何，顺便算 2 的 10 次方",
]


def main() -> None:
    print("=" * 60)
    print("Day 19 · Function Calling Agent（纯 API，无框架）")
    print("=" * 60)

    agent = FunctionCallingAgent()
    print(f"LLM 模式: {agent.client.mode} | 工具数: {len(agent.tools)}")

    queries = DEMO_QUERIES
    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]

    for q in queries:
        print("\n" + "=" * 60)
        print(f"用户: {q}")
        trace = agent.run(q)
        print(f"\n轨迹摘要: {len(trace.rounds)} 轮 | 回答: {trace.final_answer[:80]}…")

    print("\n✅ function_calling_agent.py 完成")


if __name__ == "__main__":
    main()
