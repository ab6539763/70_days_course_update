# -*- coding: utf-8 -*-
"""Day 27 · Memory 综合演示：窗口 / 摘要 / SQLite 持久化。"""

from __future__ import annotations

import sys
from pathlib import Path

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from mock_llm import build_chat_model, is_mock_mode  # noqa: E402

DB_PATH = CODE_DIR / "data" / "memory_demo.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class WindowChatMessageHistory(BaseChatMessageHistory):
    """滑动窗口记忆：仅保留最近 k 对 human/ai 消息。"""

    def __init__(self, k: int = 2) -> None:
        self._k = k
        self._inner = ChatMessageHistory()

    @property
    def messages(self) -> list[BaseMessage]:
        return self._inner.messages

    def add_message(self, message: BaseMessage) -> None:
        self._inner.add_message(message)
        self._trim()

    def clear(self) -> None:
        self._inner.clear()

    def add_user_message(self, text: str) -> None:
        self.add_message(HumanMessage(content=text))

    def add_ai_message(self, text: str) -> None:
        self.add_message(AIMessage(content=text))

    def _trim(self) -> None:
        msgs = self._inner.messages
        max_msgs = self._k * 2
        if len(msgs) > max_msgs:
            self._inner.messages = msgs[-max_msgs:]


class SummaryChatMessageHistory(BaseChatMessageHistory):
    """摘要记忆：超过阈值时将旧消息压缩为摘要文本。"""

    def __init__(self, *, max_messages: int = 4, summary_text: str = "") -> None:
        self._max_messages = max_messages
        self._summary_text = summary_text
        self._inner = ChatMessageHistory()

    @property
    def messages(self) -> list[BaseMessage]:
        return self._inner.messages

    @property
    def summary(self) -> str:
        return self._summary_text

    def add_message(self, message: BaseMessage) -> None:
        self._inner.add_message(message)
        if len(self._inner.messages) > self._max_messages:
            self._summarize_old()

    def clear(self) -> None:
        self._inner.clear()
        self._summary_text = ""

    def add_user_message(self, text: str) -> None:
        self.add_message(HumanMessage(content=text))

    def add_ai_message(self, text: str) -> None:
        self.add_message(AIMessage(content=text))

    def _summarize_old(self) -> None:
        """mock 摘要：拼接旧消息关键词（课堂可换真实 LLM 摘要链）。"""
        old = self._inner.messages[:-2]
        if not old:
            return
        parts = []
        for m in old:
            role = getattr(m, "type", "?")
            content = str(getattr(m, "content", ""))[:30]
            parts.append(f"{role}:{content}")
        self._summary_text = "历史摘要：" + " | ".join(parts)
        self._inner.messages = self._inner.messages[-2:]


def demo_chat_message_history() -> ChatMessageHistory:
  """基础 ChatMessageHistory（内存）。"""
  history = ChatMessageHistory()
  history.add_user_message("你好")
  history.add_ai_message("您好，有什么可以帮您？")
  return history


def demo_window_memory() -> WindowChatMessageHistory:
  """窗口记忆演示。"""
  history = WindowChatMessageHistory(k=2)
  pairs = [
    ("第1轮用户", "第1轮助手"),
    ("第2轮用户", "第2轮助手"),
    ("第3轮用户", "第3轮助手"),
  ]
  for user, ai in pairs:
    history.add_user_message(user)
    history.add_ai_message(ai)
  return history


def demo_summary_memory() -> SummaryChatMessageHistory:
  """摘要记忆演示。"""
  history = SummaryChatMessageHistory(max_messages=4)
  for i in range(1, 5):
    history.add_user_message(f"用户消息{i}")
    history.add_ai_message(f"助手回复{i}")
  return history


def demo_sqlite_history(session_id: str = "demo-sqlite") -> SQLChatMessageHistory:
  """SQLite 持久化 ChatMessageHistory。"""
  conn = f"sqlite:///{DB_PATH}"
  history = SQLChatMessageHistory(session_id=session_id, connection_string=conn)
  history.clear()
  history.add_message(HumanMessage(content="持久化测试用户"))
  history.add_message(AIMessage(content="持久化测试助手"))
  return history


def count_messages_in_history(history) -> int:
  return len(history.messages)


def build_memory_prompt() -> ChatPromptTemplate:
  return ChatPromptTemplate.from_messages(
    [
      ("system", "你是星火智服助手，请参考对话历史回答。"),
      MessagesPlaceholder(variable_name="history"),
      ("human", "{user_input}"),
    ]
  )


def demo_memory_overview() -> None:
  """命令行打印各 Memory 模式效果。"""
  print("=== ChatMessageHistory（内存）===")
  h1 = demo_chat_message_history()
  print(f"消息数: {len(h1.messages)}")
  for m in h1.messages:
    print(f"  [{m.type}] {m.content}")
  print()

  print("=== WindowChatMessageHistory (k=2) ===")
  h2 = demo_window_memory()
  print(f"保留消息数: {len(h2.messages)} (应为 4)")
  for m in h2.messages:
    print(f"  [{m.type}] {m.content}")
  print()

  print("=== SummaryChatMessageHistory ===")
  h3 = demo_summary_memory()
  print(f"摘要: {h3.summary}")
  print(f"当前消息数: {len(h3.messages)}")
  print()

  print("=== SQLChatMessageHistory（SQLite）===")
  h4 = demo_sqlite_history()
  print(f"DB 路径: {DB_PATH}")
  print(f"消息数: {len(h4.messages)}")
  # 重新打开验证持久化
  h4_reload = SQLChatMessageHistory(
    session_id="demo-sqlite", connection_string=f"sqlite:///{DB_PATH}"
  )
  print(f"重载后消息数: {len(h4_reload.messages)}")
  print(f"mock={is_mock_mode()}")


if __name__ == "__main__":
  demo_memory_overview()
