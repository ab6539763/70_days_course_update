# -*- coding: utf-8 -*-
"""Day 14 · ConversationSession —— 多轮对话会话管理。"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from project1.models import ChatMessage

DEFAULT_SYSTEM_PROMPT = (
    "你是星火智服内部 PoC 助手，回答简洁专业。"
    "涉及培训进度时，可引用 Day 8～14 课程内容。"
)


class ConversationSession:
    """维护 list[ChatMessage] 的多轮对话会话。"""

    def __init__(
        self,
        *,
        session_id: str | None = None,
        title: str = "未命名会话",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        messages: list[ChatMessage] | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> None:
        self.session_id = session_id or uuid4().hex[:12]
        self.title = title.strip() or "未命名会话"
        now = datetime.now(timezone.utc).isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self._messages: list[ChatMessage] = []

        if messages:
            for msg in messages:
                self._messages.append(msg)
        else:
            self._messages.append(ChatMessage.system_prompt(system_prompt))

    @property
    def messages(self) -> list[ChatMessage]:
        return list(self._messages)

    def __len__(self) -> int:
        return len(self._messages)

    def add_user_message(self, content: str) -> ChatMessage:
        msg = ChatMessage("user", content)
        self._messages.append(msg)
        self._touch()
        return msg

    def add_assistant_message(self, content: str) -> ChatMessage:
        msg = ChatMessage("assistant", content)
        self._messages.append(msg)
        self._touch()
        return msg

    def clear(self, *, keep_system: bool = True) -> int:
        """清空历史；默认保留 system 消息。返回被移除条数。"""
        before = len(self._messages)
        if keep_system:
            self._messages = [m for m in self._messages if m.is_system()]
        else:
            self._messages = []
        self._touch()
        return before - len(self._messages)

    def to_api_messages(self) -> list[dict]:
        """转为 LLM API 所需的 messages 数组（不含 created_at）。"""
        return [{"role": m.role, "content": m.content} for m in self._messages]

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [m.to_dict() for m in self._messages],
        }

    @classmethod
    def from_dict(cls, data: dict) -> ConversationSession:
        raw_messages = data.get("messages", [])
        messages = [ChatMessage.from_dict(item) for item in raw_messages]
        return cls(
            session_id=str(data.get("session_id", "")),
            title=str(data.get("title", "未命名会话")),
            messages=messages,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def summary(self) -> str:
        user_count = sum(1 for m in self._messages if m.is_user())
        assistant_count = sum(1 for m in self._messages if m.is_assistant())
        return (
            f"会话 {self.session_id} | {self.title} | "
            f"共 {len(self._messages)} 条（user={user_count}, assistant={assistant_count}）"
        )

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()
