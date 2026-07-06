# -*- coding: utf-8 -*-
"""Day 25 · PromptTemplate / ChatPromptTemplate 教学示例。"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder


# 星火智服默认 system 提示词（与 Day 14 对齐）
DEFAULT_SYSTEM_PROMPT = (
    "你是星火智服内部 PoC 助手，回答简洁专业。"
    "涉及培训进度时，可引用 Day 8～14 课程内容。"
)


def build_string_prompt() -> PromptTemplate:
    """单字符串 PromptTemplate —— 适合 completion 风格任务。"""
    return PromptTemplate(
        input_variables=["product", "language"],
        template=(
            "请将以下产品名称翻译为{language}，只输出译文：\n"
            "产品：{product}"
        ),
    )


def build_chat_prompt(*, system: str = DEFAULT_SYSTEM_PROMPT) -> ChatPromptTemplate:
    """ChatPromptTemplate —— system + 历史占位 + 当前 user。"""
    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_input}"),
        ]
    )


def build_simple_chat_prompt() -> ChatPromptTemplate:
    """最简 Chat 模板：system + human。"""
    return ChatPromptTemplate.from_messages(
        [
            ("system", DEFAULT_SYSTEM_PROMPT),
            ("human", "{user_input}"),
        ]
    )


def format_string_prompt(product: str, language: str = "英文") -> str:
    """格式化字符串模板（不调用 LLM）。"""
    return build_string_prompt().format(product=product, language=language)


def format_chat_messages(user_input: str, history: list | None = None) -> list:
    """将 ChatPromptTemplate 格式化为 LangChain Message 列表。"""
    prompt = build_chat_prompt()
    return prompt.format_messages(user_input=user_input, history=history or [])


def demo_prompt_templates() -> None:
    """命令行演示入口。"""
    print("=== PromptTemplate 示例 ===")
    print(format_string_prompt("星火智服智能客服", language="英文"))
    print()

    print("=== ChatPromptTemplate 示例 ===")
    messages = format_chat_messages("你好，我是培训生小王")
    for msg in messages:
        role = getattr(msg, "type", "unknown")
        print(f"[{role}] {msg.content}")
    print()

    print("=== 带历史的 ChatPromptTemplate ===")
    from langchain_core.messages import AIMessage, HumanMessage

    history = [
        HumanMessage(content="上一轮：介绍 LangChain"),
        AIMessage(content="LangChain 是 LLM 应用开发框架。"),
    ]
    msgs = format_chat_messages("那 ChatModel 是什么？", history=history)
    for msg in msgs:
        role = getattr(msg, "type", "unknown")
        print(f"[{role}] {msg.content[:60]}..." if len(str(msg.content)) > 60 else f"[{role}] {msg.content}")


if __name__ == "__main__":
    demo_prompt_templates()
