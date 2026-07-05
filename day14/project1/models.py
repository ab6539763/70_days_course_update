# -*- coding: utf-8 -*-
"""Day 14 · ChatMessage —— 星火智服对话消息单元（Day 8 模式复用）。"""

from __future__ import annotations

from datetime import datetime, timezone


class ChatMessage:
    """单条对话消息；与 OpenAI Chat Completions messages 数组结构对齐。"""

    VALID_ROLES: tuple[str, ...] = ("system", "user", "assistant")

    def __init__(self, role: str, content: str, created_at: str | None = None) -> None:
        self.role = self._normalize_role(role)
        self.content = self._validate_content(content)
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def _normalize_role(self, role: str) -> str:
        role = role.strip().lower()
        if role not in self.VALID_ROLES:
            allowed = ", ".join(self.VALID_ROLES)
            raise ValueError(f"非法 role「{role}」，允许值: {allowed}")
        return role

    def _validate_content(self, content: str) -> str:
        text = content.strip()
        if not text:
            raise ValueError("消息 content 不能为空。")
        return text

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
        }

    def is_user(self) -> bool:
        return self.role == "user"

    def is_assistant(self) -> bool:
        return self.role == "assistant"

    def is_system(self) -> bool:
        return self.role == "system"

    def __str__(self) -> str:
        body = ChatMessage.preview(self.content, max_len=48)
        return f"[{self.role}] {body}"

    @classmethod
    def from_dict(cls, data: dict) -> ChatMessage:
        return cls(
            role=str(data.get("role", "")),
            content=str(data.get("content", "")),
            created_at=data.get("created_at"),
        )

    @classmethod
    def system_prompt(cls, content: str) -> ChatMessage:
        return cls("system", content)

    @staticmethod
    def preview(text: str, max_len: int = 40) -> str:
        text = text.strip()
        if len(text) <= max_len:
            return text
        return text[: max_len - 1] + "…"

    @staticmethod
    def validate_role(role: str) -> bool:
        return role.strip().lower() in ChatMessage.VALID_ROLES
