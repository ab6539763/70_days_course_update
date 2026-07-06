# -*- coding: utf-8 -*-
"""星火智服 mock LLM（Day 43 Multi-Agent）。"""

from __future__ import annotations

import hashlib
import os
from typing import Any

from langchain_community.chat_models.fake import FakeListChatModel
from langchain_core.language_models.chat_models import BaseChatModel


def is_mock_mode() -> bool:
    mock_flag = os.getenv("SPARKTECH_MOCK", "").lower()
    if mock_flag in ("1", "true", "yes"):
        return True
    return not os.getenv("OPENAI_API_KEY", "").strip()


def build_mock_chat_model(responses: list[str] | None = None) -> FakeListChatModel:
    default = responses or [
        "searcher: 找到 3 条关于 LangGraph 的官方文档链接。",
        "analyst: 核心结论 — Supervisor 模式适合异构子 Agent 编排。",
        "writer: 综合报告已生成，含摘要与行动建议。",
        "supervisor: 任务完成，交付 research_report。",
    ]
    return FakeListChatModel(responses=default)


def build_chat_model(responses: list[str] | None = None, **kwargs: Any) -> BaseChatModel:
    if is_mock_mode():
        return build_mock_chat_model(responses)
    from langchain_openai import ChatOpenAI

    model = kwargs.pop("model", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    return ChatOpenAI(model=model, temperature=kwargs.pop("temperature", 0.3), **kwargs)


def stable_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:8]
