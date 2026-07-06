# -*- coding: utf-8 -*-
"""Day 45 · Mock LLM for integrated agent review (no API key required)."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any


def is_mock_mode() -> bool:
    val = os.environ.get("SPARKTECH_MOCK", "1").strip().lower()
    return val in {"1", "true", "yes", "on"}


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class AgentLLMResult:
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    mock: bool = True


class MockAgentLLM:
    """Heuristic mock that routes common agent queries to tool calls."""

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> AgentLLMResult:
        user_text = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_text = str(msg.get("content", ""))
                break

        tool_names = {t["function"]["name"] for t in tools if "function" in t}
        lower = user_text.lower()

        if "rag" in lower or "知识库" in user_text or "退款" in user_text:
            if "search_knowledge" in tool_names:
                query = re.sub(r"(查|搜索|知识库|rag)", "", user_text, flags=re.I).strip() or "退款政策"
                return AgentLLMResult(
                    tool_calls=[
                        ToolCall("search_knowledge", {"query": query}),
                    ]
                )

        if "天气" in user_text:
            city = _extract_city(user_text) or "北京"
            if "get_weather" in tool_names:
                return AgentLLMResult(tool_calls=[ToolCall("get_weather", {"city": city})])

        order_match = re.search(r"ST-\d+", user_text, re.I)
        if order_match and "lookup_order" in tool_names:
            return AgentLLMResult(
                tool_calls=[ToolCall("lookup_order", {"order_id": order_match.group(0).upper()})]
            )

        calc_match = re.search(r"(\d+)\s*([+\-*/])\s*(\d+)", user_text)
        if calc_match and "calc" in tool_names:
            return AgentLLMResult(
                tool_calls=[
                    ToolCall(
                        "calc",
                        {
                            "expression": f"{calc_match.group(1)}{calc_match.group(2)}{calc_match.group(3)}"
                        },
                    )
                ]
            )

        if any("tool" in str(m.get("role", "")) for m in messages[-3:]):
            last_tool = _last_tool_result(messages)
            return AgentLLMResult(content=f"根据工具结果：{last_tool}")

        return AgentLLMResult(content=f"[mock] 收到：{user_text[:80]}。可尝试问天气、订单 ST-10086、知识库退款、或计算 2+3。")


def _extract_city(text: str) -> str | None:
    for city in ("北京", "上海", "广州", "深圳", "杭州", "成都"):
        if city in text:
            return city
    return None


def _last_tool_result(messages: list[dict[str, Any]]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "tool":
            return str(msg.get("content", ""))[:200]
    return "无工具结果"


def build_agent_llm() -> MockAgentLLM:
    return MockAgentLLM()
