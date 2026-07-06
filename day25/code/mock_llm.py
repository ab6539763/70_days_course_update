# -*- coding: utf-8 -*-
"""星火智服 LangChain mock 工具 —— 无 API Key 时使用 FakeListChatModel。"""

from __future__ import annotations

import hashlib
import os
from typing import Any

from langchain_community.chat_models.fake import FakeListChatModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage


def is_mock_mode() -> bool:
    """判断是否进入 mock 模式（课堂默认）。"""
    mock_flag = os.getenv("SPARKTECH_MOCK", "").lower()
    if mock_flag in ("1", "true", "yes"):
        return True
    return not os.getenv("OPENAI_API_KEY", "").strip()


def mock_reply_for_user(user_text: str, *, call_index: int = 1, model: str = "gpt-4o-mini") -> str:
    """生成与 Day 14 mock 文案风格一致的回复。"""
    digest = hashlib.md5(user_text.encode()).hexdigest()[:8]
    preview = user_text.strip()
    if len(preview) > 40:
        preview = preview[:39] + "…"
    return (
        f"[mock/{model}] 已收到你的第 {call_index} 轮提问："
        f"「{preview}」。（mock_id={digest}）"
    )


def build_mock_chat_model(
    responses: list[str] | None = None,
    *,
    model_name: str = "fake-list-chat-model",
) -> FakeListChatModel:
    """构造可循环使用的 FakeListChatModel。"""
    default = responses or [
        "[mock/LC] 你好，我是星火智服 LangChain 助手。",
        "[mock/LC] 已记录上下文，请继续提问。",
        "[mock/LC] 感谢使用，输入 /exit 可退出。",
    ]
    return FakeListChatModel(responses=default)


def build_chat_model(
    responses: list[str] | None = None,
    **kwargs: Any,
) -> BaseChatModel:
    """
    统一 ChatModel 工厂。

    - mock：FakeListChatModel
    - live：ChatOpenAI（需 OPENAI_API_KEY）
    """
    if is_mock_mode():
        return build_mock_chat_model(responses)

    from langchain_openai import ChatOpenAI

    model = kwargs.pop("model", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    temperature = kwargs.pop("temperature", 0.7)
    return ChatOpenAI(model=model, temperature=temperature, **kwargs)


def last_user_text(messages: list[BaseMessage]) -> str:
    """从消息列表中取最后一条用户输入。"""
    for msg in reversed(messages):
        role = getattr(msg, "type", None) or getattr(msg, "role", "")
        if role in ("human", "user"):
            return str(getattr(msg, "content", ""))
    return ""
