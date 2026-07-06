# -*- coding: utf-8 -*-
"""星火智服 LangChain mock 工具（Day 26 复用）。"""

from __future__ import annotations

import os
from typing import Any

from langchain_community.chat_models.fake import FakeListChatModel
from langchain_core.language_models.chat_models import BaseChatModel


def is_mock_mode() -> bool:
    mock_flag = os.getenv("SPARKTECH_MOCK", "").lower()
    if mock_flag in ("1", "true", "yes"):
        return True
    return not os.getenv("OPENAI_API_KEY", "").strip()


def build_mock_chat_model(
    responses: list[str] | None = None,
) -> FakeListChatModel:
    default = responses or ["[mock/LCEL] 默认回复"]
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
