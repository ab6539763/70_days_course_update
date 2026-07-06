# -*- coding: utf-8 -*-
"""
Day 44 · Agent + MCP 工具编排

Agent 根据用户问题选择 MCP 工具，汇总工具结果后生成回答。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from mcp_client_demo import SparkTechMCPClient
from mock_llm import build_chat_model


@dataclass
class AgentStep:
    action: str
    detail: str


@dataclass
class AgentTrace:
    question: str
    steps: list[AgentStep] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    answer: str = ""


def _needs_kb(question: str) -> bool:
    keys = ("退款", "api", "key", "密钥", "知识", "政策")
    q = question.lower()
    return any(k in q for k in keys)


def _needs_ticket(question: str) -> bool:
    return bool(re.search(r"INC-\d+", question, re.I)) or "工单" in question


def plan_tools(question: str) -> list[tuple[str, dict]]:
    planned: list[tuple[str, dict]] = []
    if _needs_kb(question):
        planned.append(("kb_search", {"query": question}))
    if _needs_ticket(question):
        m = re.search(r"(INC-\d+[-\w]*)", question, re.I)
        tid = m.group(1) if m else "INC-UNKNOWN"
        planned.append(("ticket_status", {"ticket_id": tid}))
    if not planned:
        planned.append(("kb_search", {"query": question}))
    return planned


def run_agent_with_mcp(question: str) -> AgentTrace:
    client = SparkTechMCPClient()
    trace = AgentTrace(question=question)
    trace.steps.append(AgentStep("plan", f"tools={[t[0] for t in plan_tools(question)]}"))

    context_parts: list[str] = []
    for tool_name, args in plan_tools(question):
        result = client.call(tool_name, **args)
        parsed = result.parsed
        trace.tool_results.append({"tool": tool_name, "args": args, "result": parsed})
        trace.steps.append(AgentStep("tool", f"{tool_name}({json.dumps(args, ensure_ascii=False)})"))
        context_parts.append(f"[{tool_name}]\n{json.dumps(parsed, ensure_ascii=False)}")

    llm = build_chat_model()
    system = SystemMessage(
        content="你是星火智服助手。仅根据 MCP 工具返回的事实回答，简洁专业。"
    )
    user = HumanMessage(
        content=f"用户问题: {question}\n\n工具结果:\n" + "\n\n".join(context_parts)
    )
    answer = str(llm.invoke([system, user]).content)
    trace.answer = answer
    trace.steps.append(AgentStep("answer", f"len={len(answer)}"))
    return trace


def main() -> None:
    print("=== Day 44 Agent with MCP ===\n")
    q = "工单 INC-2026-042 进展如何？另外 API Key 怎么申请？"
    trace = run_agent_with_mcp(q)
    print(f"Q: {trace.question}\n")
    for step in trace.steps:
        print(f"  [{step.action}] {step.detail}")
    print(f"\nA: {trace.answer}")


if __name__ == "__main__":
    main()
