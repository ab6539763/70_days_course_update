# -*- coding: utf-8 -*-
"""
Day 13 下午 · 类型注解（typing）

覆盖：
- 基础类型、Optional、Union（| 语法）
- list/dict 泛型
- Callable、TypeVar、Protocol
- TypedDict 与 LLM messages 结构

运行：cd day13/code && python3 typing_demo.py
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal, Protocol, TypedDict, TypeVar

T = TypeVar("T")


# ---------------------------------------------------------------------------
# 第一章：基础注解
# ---------------------------------------------------------------------------


def normalize_phone(raw: str) -> str:
    """返回仅含数字的手机号字符串。"""
    digits = "".join(ch for ch in raw if ch.isdigit())
    return digits


def find_contact(
    contacts: list[dict[str, str]],
    name: str,
) -> dict[str, str] | None:
    for c in contacts:
        if c.get("name") == name:
            return c
    return None


# ---------------------------------------------------------------------------
# 第二章：TypedDict —— LLM messages 契约
# ---------------------------------------------------------------------------


class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionUsage(TypedDict, total=False):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


def build_messages(user_prompt: str, *, system: str = "") -> list[ChatMessage]:
    messages: list[ChatMessage] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user_prompt})
    return messages


# ---------------------------------------------------------------------------
# 第三章：Callable 与 TypeVar
# ---------------------------------------------------------------------------


def apply_twice(func: Callable[[T], T], value: T) -> T:
    return func(func(value))


def double(x: int) -> int:
    return x * 2


# ---------------------------------------------------------------------------
# 第四章：Protocol（结构化子类型）
# ---------------------------------------------------------------------------


class Generatable(Protocol):
    """任何有 generate(prompt) 方法的对象都满足此协议。"""

    def generate(self, prompt: str) -> str: ...


@dataclass
class MockModel:
    name: str

    def generate(self, prompt: str) -> str:
        return f"[{self.name}] {prompt[:20]}"


def run_prompt(model: Generatable, prompt: str) -> str:
    """接受任何满足 Protocol 的模型，无需继承同一基类。"""
    return model.generate(prompt)


# ---------------------------------------------------------------------------
# 第五章：类型收窄（isinstance / Literal）
# ---------------------------------------------------------------------------


Role = Literal["system", "user", "assistant"]


def role_label(role: Role) -> str:
    labels: dict[Role, str] = {
        "system": "系统",
        "user": "用户",
        "assistant": "助手",
    }
    return labels[role]


# ---------------------------------------------------------------------------
# 演示
# ---------------------------------------------------------------------------


def demo_typed_messages() -> None:
    print("\n--- §1 TypedDict messages ---")
    msgs = build_messages(
        "解释 retry 装饰器",
        system="你是星火智服技术助手。",
    )
    print(json.dumps(msgs, ensure_ascii=False, indent=2))


def demo_callable() -> None:
    print("\n--- §2 Callable + TypeVar ---")
    print(f"apply_twice(double, 3) = {apply_twice(double, 3)}")


def demo_protocol() -> None:
    print("\n--- §3 Protocol ---")
    model = MockModel(name="gpt-mock")
    print(run_prompt(model, "Day 13 typing 验收"))


def demo_optional() -> None:
    print("\n--- §4 Optional 收窄 ---")
    contacts = [{"name": "陈晓", "phone": "13800138001"}]
    found = find_contact(contacts, "陈晓")
    if found is not None:
        print(f"找到: {found['phone']}")
    missing = find_contact(contacts, "不存在")
    print(f"未找到: {missing}")


def main() -> None:
    print("=" * 60)
    print("Day 13 下午 · typing_demo.py")
    print("=" * 60)
    demo_typed_messages()
    demo_callable()
    demo_protocol()
    demo_optional()
    print(f"\n手机号归一化: {normalize_phone('138-0013-8001')}")
    print("\n✅ typing_demo.py 完成")


if __name__ == "__main__":
    main()
