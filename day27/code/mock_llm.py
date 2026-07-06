# -*- coding: utf-8 -*-
"""星火智服 LangChain mock 工具（Day 27 复用）。"""

from __future__ import annotations

import hashlib
import os
from typing import Any

from langchain_community.chat_models.fake import FakeListChatModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage


def is_mock_mode() -> bool:
    mock_flag = os.getenv("SPARKTECH_MOCK", "").lower()
    if mock_flag in ("1", "true", "yes"):
        return True
    return not os.getenv("OPENAI_API_KEY", "").strip()


def mock_reply_for_user(user_text: str, *, call_index: int = 1) -> str:
    digest = hashlib.md5(user_text.encode()).hexdigest()[:8]
    preview = user_text.strip()[:40]
    return (
        f"[mock/Memory] 第 {call_index} 轮：「{preview}」"
        f"（session 已记录历史，mock_id={digest}）"
    )


def build_mock_chat_model(responses: list[str] | None = None) -> FakeListChatModel:
    default = responses or [
        "[mock] 你好，我会记住本轮对话。",
        "[mock] 已读取历史上下文，请继续。",
        "[mock] 多轮记忆演示正常。",
    ]
    return FakeListChatModel(responses=default)


def build_chat_model(
    responses: list[str] | None = None,
    **kwargs: Any,
) -> BaseChatModel:
    if is_mock_mode():
        return build_mock_chat_model(responses)
    from langchain_openai import ChatOpenAI

    model = kwargs.pop("model", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    return ChatOpenAI(model=model, temperature=kwargs.pop("temperature", 0.7), **kwargs)


def last_user_text(messages: list[BaseMessage]) -> str:
    for msg in reversed(messages):
        role = getattr(msg, "type", "")
        if role in ("human", "user"):
            return str(getattr(msg, "content", ""))
    return ""
