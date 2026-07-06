# -*- coding: utf-8 -*-
"""Day 14 · 星火智服命令行多轮对话助手 —— 包入口。"""

from project1.commands import CommandHandler, CommandResult, HELP_TEXT
from project1.llm_client import ChatCompletionResult, LLMClient, LLMClientError
from project1.models import ChatMessage
from project1.session import ConversationSession, DEFAULT_SYSTEM_PROMPT
from project1.storage import load_session, save_session

__version__ = "1.0.0"

__all__ = [
    "ChatCompletionResult",
    "ChatMessage",
    "CommandHandler",
    "CommandResult",
    "ConversationSession",
    "DEFAULT_SYSTEM_PROMPT",
    "HELP_TEXT",
    "LLMClient",
    "LLMClientError",
    "load_session",
    "save_session",
    "__version__",
]
