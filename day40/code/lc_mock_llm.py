# -*- coding: utf-8 -*-
"""Day 40 · LangChain mock / live ChatModel 工厂。"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from langchain_community.chat_models.fake import FakeListChatModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolCall


def is_mock_mode() -> bool:
    flag = os.getenv("SPARKTECH_MOCK", "").lower()
    if flag in ("1", "true", "yes"):
        return True
    return not os.getenv("OPENAI_API_KEY", "").strip()


def _last_user(messages: list[BaseMessage]) -> str:
    for m in reversed(messages):
        if m.type == "human":
            return str(m.content)
    return ""


def _has_tool_results(messages: list[BaseMessage]) -> bool:
    return any(m.type == "tool" for m in messages)


def _tool_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    return [m for m in messages if m.type == "tool"]


def _tool_names(messages: list[BaseMessage]) -> list[str]:
    names: list[str] = []
    for m in _tool_messages(messages):
        name = getattr(m, "name", None) or ""
        if not name:
            # 从内容推断（部分 ToolMessage 无 name 字段）
            try:
                data = json.loads(str(m.content))
                if "team_label" in data or "team" in data:
                    name = "route_ticket"
                elif "snippets" in data:
                    name = "search_kb"
                elif "result" in data and "expression" in data:
                    name = "calculator"
                elif "intent" in data and "confidence" in data:
                    name = "classify_ticket"
            except json.JSONDecodeError:
                pass
        names.append(name)
    return names


def _plan_tool_calls(user_text: str) -> list[ToolCall]:
    """启发式 mock tool_calls。"""
    calls: list[ToolCall] = []

    if any(k in user_text for k in ("退款", "退费", "账单")):
        calls.append(
            ToolCall(
                name="classify_ticket",
                args={"text": user_text[:120]},
                id="call_classify_1",
            )
        )
    elif any(k in user_text for k in ("计算", "等于", "+", "*", "优先级")) or re.search(
        r"\d+\s*[\+\-\*\/]\s*\d+", user_text
    ):
        expr = re.search(r"(\d+\s*[\*\+\-\/]\s*\d+(?:\s*[\+\-]\s*\d+)?)", user_text)
        if not expr:
            expr = re.search(r"([\d\s+\-*/().]+)", user_text)
        calls.append(
            ToolCall(
                name="calculator",
                args={"expression": (expr.group(1).strip() if expr else "2+3")},
                id="call_calc_1",
            )
        )
    elif any(k in user_text for k in ("政策", "知识", "怎么", "如何", "退款政策")):
        calls.append(
            ToolCall(
                name="search_kb",
                args={"query": user_text[:60], "limit": 2},
                id="call_kb_1",
            )
        )
    else:
        calls.append(
            ToolCall(
                name="classify_ticket",
                args={"text": user_text[:120] or "一般咨询"},
                id="call_classify_default",
            )
        )
    return calls


def _finalize_from_tools(messages: list[BaseMessage]) -> str:
    parts: list[str] = []
    for m in messages:
        if m.type != "tool":
            continue
        try:
            data = json.loads(str(m.content))
        except json.JSONDecodeError:
            data = {"raw": str(m.content)}
        name = getattr(m, "name", "tool")
        if name == "classify_ticket":
            parts.append(f"意图={data.get('intent')}（置信度 {data.get('confidence')}）")
        elif name == "route_ticket":
            parts.append(f"已路由至 {data.get('team_label')}，SLA {data.get('sla_hours')}h")
        elif name == "search_kb":
            titles = [s.get("title") for s in data.get("snippets", [])]
            parts.append(f"知识库：{'、'.join(titles) or '无'}")
        elif name == "calculator":
            parts.append(f"{data.get('expression')} = {data.get('result')}")
        else:
            parts.append(json.dumps(data, ensure_ascii=False)[:80])
    return "[mock/LC Agent] " + "；".join(parts) if parts else "[mock] 处理完成。"


class MockToolChatModel(BaseChatModel):
    """支持 bind_tools 的 mock ChatModel。"""

    _bound_tool_names: set[str] = set()

    @property
    def _llm_type(self) -> str:
        return "mock_tool_chat"

    def bind_tools(self, tools, **kwargs: Any):  # noqa: ANN001
        """create_tool_calling_agent 需要 bind_tools；记录可用工具名。"""
        self._bound_tool_names = {getattr(t, "name", str(t)) for t in tools}
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        from langchain_core.outputs import ChatGeneration, ChatResult

        user = _last_user(messages)
        names = _tool_names(messages)
        if _tool_messages(messages):
            # 分类后补路由
            if (
                "classify_ticket" in names
                and "route_ticket" not in names
                and "route_ticket" in self._bound_tool_names
            ):
                try:
                    classify_msg = _tool_messages(messages)[names.index("classify_ticket")]
                    data = json.loads(str(classify_msg.content))
                except (json.JSONDecodeError, ValueError):
                    data = {}
                if data.get("intent"):
                    tc = ToolCall(
                        name="route_ticket",
                        args={
                            "intent": data["intent"],
                            "customer_tier": "vip" if "vip" in user.lower() else "standard",
                        },
                        id="call_route_1",
                    )
                    msg = AIMessage(content="", tool_calls=[tc])
                else:
                    msg = AIMessage(content=_finalize_from_tools(messages))
            else:
                msg = AIMessage(content=_finalize_from_tools(messages))
        else:
            tcs = _plan_tool_calls(user)
            msg = AIMessage(content="", tool_calls=tcs)

        return ChatResult(generations=[ChatGeneration(message=msg)])


def build_chat_model(**kwargs: Any) -> BaseChatModel:
    if is_mock_mode():
        return MockToolChatModel()
    from langchain_openai import ChatOpenAI

    model = kwargs.pop("model", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    return ChatOpenAI(model=model, temperature=kwargs.pop("temperature", 0.2), **kwargs)


def build_fake_list_model(responses: list[str]) -> FakeListChatModel:
    return FakeListChatModel(responses=responses)
