# -*- coding: utf-8 -*-
"""
Day 40 · 搜索 + 计算组合 Agent 示例

演示 @tool + AgentExecutor 的多工具协作。

运行：cd day40/code && python3 search_calc_agent.py
"""

from __future__ import annotations

import json

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from lc_tools import get_search_calc_tools
from lc_mock_llm import build_chat_model, is_mock_mode


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是星火智服助手。需要查知识库时用 search_kb，需要算数时用 calculator，"
            "需要判断工单类型时用 classify_ticket。中文简洁回答。",
        ),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)


def build_search_calc_agent(*, verbose: bool = False) -> AgentExecutor:
    llm = build_chat_model()
    tools = get_search_calc_tools()
    agent = create_tool_calling_agent(llm, tools, PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


def demo_refund_policy() -> dict:
    """查退款政策 + 分类。"""
    agent = build_search_calc_agent()
    return agent.invoke({"input": "查一下退款政策，客户说要退费"})


def demo_calc_sla() -> dict:
    """计算 SLA 相关表达式。"""
    agent = build_search_calc_agent()
    return agent.invoke({"input": "请用 calculator 计算 4*5+3"})


def main() -> None:
    print("=" * 60)
    print(f"Day 40 · search_calc_agent（mock={is_mock_mode()}）")
    print("=" * 60)

    print("\n[Demo 1] 退款政策检索")
    r1 = demo_refund_policy()
    print(f"输出: {r1['output']}")
    print(f"步骤: {len(r1.get('intermediate_steps', []))}")

    print("\n[Demo 2] 计算演示")
    r2 = demo_calc_sla()
    print(f"输出: {r2['output']}")

    print("\n✅ search_calc_agent.py 完成")


if __name__ == "__main__":
    main()
