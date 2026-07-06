# -*- coding: utf-8 -*-
"""
Day 45 · Week 5 Agent 综合复盘助手

整合 Day 39–44 Agent 能力：
- ReAct 式 tool 循环
- RAG 检索工具（mock）
- 订单 / 天气 / 计算工具
- 会话裁剪与轨迹记录

运行：cd day45/code && python3 integrated_agent_review.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mock_llm import AgentLLMResult, MockAgentLLM, ToolCall, build_agent_llm, is_mock_mode

CODE_DIR = Path(__file__).resolve().parent
MAX_ROUNDS = 4
MAX_MESSAGES = 24

SYSTEM_PROMPT = """你是星火智服 Week 5 Agent 综合复盘助手。
需要实时数据、知识库或计算时请调用工具；拿到结果后用简洁中文回答。"""

KNOWLEDGE_SNIPPETS: dict[str, str] = {
    "退款": "退款政策：签收 7 日内可无理由退款；定制商品除外。",
    "api": "API Key 申请：登录控制台 → 开发者中心 → 创建应用 → 复制 Key。",
    "sla": "SLA：工作日 9:00–18:00 工单 4 小时内首次响应。",
}


@dataclass
class AgentTrace:
    user_query: str
    rounds: list[dict[str, Any]] = field(default_factory=list)
    final_answer: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_query": self.user_query,
            "rounds": self.rounds,
            "final_answer": self.final_answer,
        }


class ConversationSession:
    def __init__(self, system_prompt: str = SYSTEM_PROMPT) -> None:
        self._messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    @property
    def message_count(self) -> int:
        return len(self._messages)

    def add_user(self, text: str) -> None:
        self._messages.append({"role": "user", "content": text.strip()})
        self._trim()

    def add_assistant(self, content: str, tool_calls: list[ToolCall] | None = None) -> None:
        msg: dict[str, Any] = {"role": "assistant", "content": content}
        if tool_calls:
            msg["tool_calls"] = [
                {
                    "id": f"call_{i}",
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.arguments, ensure_ascii=False)},
                }
                for i, tc in enumerate(tool_calls)
            ]
        self._messages.append(msg)
        self._trim()

    def add_tool(self, name: str, result: str) -> None:
        self._messages.append({"role": "tool", "tool_call_id": name, "name": name, "content": result})
        self._trim()

    def to_messages(self) -> list[dict[str, Any]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages = self._messages[:1]

    def _trim(self) -> None:
        if len(self._messages) <= MAX_MESSAGES:
            return
        system = self._messages[:1]
        tail = self._messages[-(MAX_MESSAGES - 1) :]
        self._messages = system + tail


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[dict[str, Any]], str]] = {
            "get_weather": self._weather,
            "lookup_order": self._order,
            "calc": self._calc,
            "search_knowledge": self._knowledge,
        }

    def schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "查询城市天气",
                    "parameters": {
                        "type": "object",
                        "properties": {"city": {"type": "string"}},
                        "required": ["city"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "lookup_order",
                    "description": "查询订单状态",
                    "parameters": {
                        "type": "object",
                        "properties": {"order_id": {"type": "string"}},
                        "required": ["order_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calc",
                    "description": "数学计算",
                    "parameters": {
                        "type": "object",
                        "properties": {"expression": {"type": "string"}},
                        "required": ["expression"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "检索企业知识库",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                },
            },
        ]

    def list_tools(self) -> list[str]:
        return sorted(self._handlers.keys())

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        handler = self._handlers.get(name)
        if not handler:
            return f"[error] 未知工具: {name}"
        try:
            return handler(arguments)
        except Exception as exc:  # noqa: BLE001
            return f"[error] {name}: {exc}"

    def _weather(self, args: dict[str, Any]) -> str:
        city = str(args.get("city", "北京"))
        return f"{city}：晴，26°C，湿度 58%（mock_weather_api）"

    def _order(self, args: dict[str, Any]) -> str:
        oid = str(args.get("order_id", "ST-10086")).upper()
        return f"订单 {oid}：已发货，预计 2026-07-08 送达（mock_erp）"

    def _calc(self, args: dict[str, Any]) -> str:
        expr = str(args.get("expression", "0"))
        if not re.fullmatch(r"[\d+\-*/().\s]+", expr):
            return "[error] 表达式含非法字符"
        try:
            return str(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307
        except Exception:
            return "[error] 计算失败"

    def _knowledge(self, args: dict[str, Any]) -> str:
        query = str(args.get("query", "")).lower()
        for key, snippet in KNOWLEDGE_SNIPPETS.items():
            if key in query:
                return snippet
        return "未找到相关知识片段（mock_kb）"


class IntegratedAgentReview:
    """Week 5 Agent 综合复盘：多轮 + 工具环 + 轨迹。"""

    def __init__(self, llm: MockAgentLLM | None = None) -> None:
        self.llm = llm or build_agent_llm()
        self.tools = ToolRegistry()
        self.session = ConversationSession()
        self.verbose = True

    @property
    def is_mock_mode(self) -> bool:
        return is_mock_mode()

    def run(self, user_query: str) -> AgentTrace:
        trace = AgentTrace(user_query=user_query)
        self.session.add_user(user_query)
        messages = self.session.to_messages()
        schemas = self.tools.schemas()

        for round_idx in range(1, MAX_ROUNDS + 1):
            result = self.llm.chat(messages, schemas)
            round_log: dict[str, Any] = {"round": round_idx, "tool_calls": []}

            if result.tool_calls:
                self.session.add_assistant("", result.tool_calls)
                for tc in result.tool_calls:
                    out = self.tools.execute(tc.name, tc.arguments)
                    self.session.add_tool(tc.name, out)
                    round_log["tool_calls"].append({"name": tc.name, "args": tc.arguments, "result": out})
                messages = self.session.to_messages()
                trace.rounds.append(round_log)
                continue

            answer = result.content or "[mock] 无回复"
            self.session.add_assistant(answer)
            trace.final_answer = answer
            trace.rounds.append(round_log)
            return trace

        trace.final_answer = "[agent] 超过最大轮次，请简化问题。"
        return trace

    def handle_user_input(self, text: str) -> str:
        trace = self.run(text)
        return trace.final_answer


def repl() -> None:
    agent = IntegratedAgentReview()
    mode = "mock" if agent.is_mock_mode else "live"
    print(f"=== Day 45 Integrated Agent Review ({mode}) ===")
    print("命令：/tools /clear /trace /exit")
    last_trace: AgentTrace | None = None

    while True:
        try:
            user = input("\n你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break
        if not user:
            continue
        if user == "/exit":
            break
        if user == "/clear":
            agent.session.clear()
            print("会话已清空。")
            continue
        if user == "/tools":
            print("工具：", ", ".join(agent.tools.list_tools()))
            continue
        if user == "/trace" and last_trace:
            print(json.dumps(last_trace.to_dict(), ensure_ascii=False, indent=2))
            continue

        last_trace = agent.run(user)
        print(f"助手> {last_trace.final_answer}")


def main() -> None:
    os.environ.setdefault("SPARKTECH_MOCK", "1")
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        agent = IntegratedAgentReview()
        for q in ("上海天气", "查订单 ST-10086", "知识库 退款政策", "计算 12+8"):
            t = agent.run(q)
            print(f"[demo] Q: {q} -> {t.final_answer}")
        return
    repl()


if __name__ == "__main__":
    main()
