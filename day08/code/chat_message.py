# -*- coding: utf-8 -*-
"""Day 8 主实战：ChatMessage 类 —— 星火智服对话消息单元。

运行：python3 chat_message.py

为 Day 14 命令行 AI 助手预埋统一消息结构：
  - role: system | user | assistant（白名单校验）
  - content: 非空文本
  - to_dict / from_dict 与 JSON 互操作
  - __str__ 便于 REPL 打印历史

OpenAI Chat Completions API 的 messages 数组与本类 to_dict() 结构对齐，
日后接 API 时可直接 [m.to_dict() for m in messages]。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone


class ChatMessage:
    """单条对话消息 —— 星火智服多轮对话的最小单元。"""

    # 类属性：所有实例共享的合法 role 枚举（与主流 LLM API 一致）
    VALID_ROLES: tuple[str, ...] = ("system", "user", "assistant")

    def __init__(self, role: str, content: str, created_at: str | None = None) -> None:
        """构造消息；role 与 content 均做校验，非法则 ValueError。"""
        self.role = self._normalize_role(role)
        self.content = self._validate_content(content)
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def _normalize_role(self, role: str) -> str:
        """实例内部：规范化并校验 role。"""
        role = role.strip().lower()
        if role not in self.VALID_ROLES:
            allowed = ", ".join(self.VALID_ROLES)
            raise ValueError(f"非法 role「{role}」，允许值: {allowed}")
        return role

    def _validate_content(self, content: str) -> str:
        """实例内部：content 不得为空（含纯空白）。"""
        text = content.strip()
        if not text:
            raise ValueError("消息 content 不能为空。")
        return text

    # ----- 实例方法 -----

    def to_dict(self) -> dict:
        """序列化为 dict，供 json.dump 或 API 请求体使用。"""
        return {
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
        }

    def is_user(self) -> bool:
        """是否为用户消息。"""
        return self.role == "user"

    def is_assistant(self) -> bool:
        """是否为助手回复。"""
        return self.role == "assistant"

    def is_system(self) -> bool:
        """是否为系统提示词。"""
        return self.role == "system"

    def __str__(self) -> str:
        """REPL 打印友好格式；长文由 preview 截断。"""
        body = ChatMessage.preview(self.content, max_len=48)
        return f"[{self.role}] {body}"

    # ----- 类方法 -----

    @classmethod
    def from_dict(cls, data: dict) -> ChatMessage:
        """从 JSON 单条记录或 API 响应构造 ChatMessage。"""
        return cls(
            role=str(data.get("role", "")),
            content=str(data.get("content", "")),
            created_at=data.get("created_at"),
        )

    @classmethod
    def system_prompt(cls, content: str) -> ChatMessage:
        """类方法工厂：快速创建 system 消息（Day 14 初始化会话常用）。"""
        return cls("system", content)

    @classmethod
    def merge_system_prompts(cls, messages: list[ChatMessage]) -> str:
        """类方法：合并列表中所有 system 消息的 content（选做作业 X2）。"""
        parts = [m.content for m in messages if m.is_system()]
        return "\n".join(parts)

    # ----- 静态方法 -----

    @staticmethod
    def preview(text: str, max_len: int = 40) -> str:
        """静态方法：截断长文本用于日志/打印，不依赖具体消息实例。"""
        text = text.strip()
        if len(text) <= max_len:
            return text
        return text[: max_len - 1] + "…"

    @staticmethod
    def validate_role(role: str) -> bool:
        """静态方法：判断 role 字符串是否在白名单内（不抛异常）。"""
        return role.strip().lower() in ChatMessage.VALID_ROLES


def build_demo_conversation() -> list[ChatMessage]:
    """构造三轮演示对话 —— 模拟星火智服 CLI 片段。"""
    return [
        ChatMessage(
            "system",
            "你是星火智服内部助手，回答简洁专业。涉及通讯录时提示用户使用 contacts.json。",
        ),
        ChatMessage("user", "通讯录数据存在哪里？Day 7 和 Day 8 有什么区别？"),
        ChatMessage(
            "assistant",
            "Week1 通讯录存在 day07/code/contacts.json，记录为 list[dict]。"
            "Day8 起用 Contact 类封装单条记录，校验与展示内聚在类中；"
            "Day14 命令行助手将用 ChatMessage 管理对话历史。",
        ),
    ]


def demo_validation() -> None:
    """演示非法 role / 空 content 被拒绝。"""
    print("--- 校验演示 ---")
    cases = [
        ("bot", "你好"),
        ("user", "   "),
    ]
    for role, content in cases:
        try:
            ChatMessage(role, content)
        except ValueError as exc:
            print(f"  拒绝 ChatMessage({role!r}, ...): {exc}")


def main() -> None:
    print("\n星火科技 Day 8 · ChatMessage chat_message.py")
    print("小陈：「消息结构今天定稿，Day 14 直接复用。」\n")

    messages = build_demo_conversation()

    print("--- 三轮对话 __str__ ---")
    for msg in messages:
        print(msg)

    print("\n--- JSON 序列化（Day 14 history.json 预览）---")
    payload = [m.to_dict() for m in messages]
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    print("\n--- from_dict 往返 ---")
    restored = ChatMessage.from_dict(payload[1])
    print(restored)
    assert restored.role == "user"

    demo_validation()

    print("\n--- 静态工具 ---")
    print(f"preview: {ChatMessage.preview('这是一段很长的用户问题' * 3)}")
    print(f"validate_role('assistant'): {ChatMessage.validate_role('assistant')}")

    print("\n小结：list[ChatMessage] + while REPL = Day 14 星火智服助手内核。")


if __name__ == "__main__":
    main()
