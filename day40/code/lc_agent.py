# -*- coding: utf-8 -*-
"""
Day 40 · LangChain Tool Calling Agent

create_tool_calling_agent + AgentExecutor 实现工单路由。

运行：cd day40/code && python3 lc_agent.py
"""

from __future__ import annotations

import json
from typing import Any

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from lc_tools import get_ticket_routing_tools
from lc_mock_llm import build_chat_model, is_mock_mode


SYSTEM_PROMPT = """你是星火智服 Phase3 工单路由助手。
根据用户描述，按需调用工具完成：知识检索、意图分类、路由分配、优先级计算。
用简洁中文汇总结果。不要编造工具未返回的数据。"""


def build_ticket_agent(*, verbose: bool = False, max_iterations: int = 6) -> AgentExecutor:
    """构建工单路由 AgentExecutor。"""
    llm = build_chat_model()
    tools = get_ticket_routing_tools()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=max_iterations,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


def run_ticket_routing(query: str, *, verbose: bool = False) -> dict[str, Any]:
    """执行一次工单路由。"""
    executor = build_ticket_agent(verbose=verbose)
    result = executor.invoke({"input": query})
    return {
        "input": query,
        "output": result.get("output", ""),
        "steps": len(result.get("intermediate_steps", [])),
        "mode": "mock" if is_mock_mode() else "live",
        "intermediate_steps": [
            {"tool": step[0].tool, "input": step[0].tool_input, "output": str(step[1])[:200]}
            for step in result.get("intermediate_steps", [])
        ],
    }


def main() -> None:
    print("=" * 60)
    print(f"Day 40 · LangChain AgentExecutor（mock={is_mock_mode()}）")
    print("=" * 60)

    queries = [
        "VIP 客户申请退款，订单已扣款请加急",
        "请问退款政策是什么？",
    ]
    for q in queries[:1]:
        print(f"\n>>> {q}")
        out = run_ticket_routing(q, verbose=True)
        print(f"\n输出: {out['output']}")
        print(f"工具步数: {out['steps']}")

    print("\n✅ lc_agent.py 完成")


if __name__ == "__main__":
    main()
