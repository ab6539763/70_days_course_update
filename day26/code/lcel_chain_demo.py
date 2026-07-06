# -*- coding: utf-8 -*-
"""Day 26 · LCEL 管道演示：Runnable、OutputParser、Passthrough、Parallel。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from pydantic import BaseModel, Field

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from mock_llm import build_chat_model, is_mock_mode  # noqa: E402


class TicketSummary(BaseModel):
    """工单摘要结构化输出（Pydantic v2 + JsonOutputParser）。"""

    ticket_id: str = Field(description="工单编号")
    sentiment: str = Field(description="情绪：positive/neutral/negative")
    summary: str = Field(description="一句话摘要")


def build_simple_lcel_chain():
    """最简 LCEL：prompt | llm | StrOutputParser。"""
    prompt = ChatPromptTemplate.from_messages(
        [("human", "用一句话回答：{question}")]
    )
    llm = build_chat_model(
        responses=[
            "LangChain 是用于构建 LLM 应用的开发框架。",
            "LCEL 使用管道符 | 组合 Runnable 组件。",
        ]
    )
    return prompt | llm | StrOutputParser()


def build_json_chain():
    """JSON 输出链：mock 时 LLM 返回 JSON 字符串。"""
    parser = JsonOutputParser()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "分析工单 {ticket_id}，返回 JSON，字段含 ticket_id、status、priority。"
                "只输出 JSON。\n{format_instructions}",
            )
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    llm = build_chat_model(
        responses=[
            '{"ticket_id": "TK-100", "status": "open", "priority": "high"}',
            '{"ticket_id": "TK-101", "status": "closed", "priority": "low"}',
        ]
    )
    return prompt | llm | parser


def build_pydantic_chain():
    """Pydantic 结构化解析链。"""
    parser = JsonOutputParser(pydantic_object=TicketSummary)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "工单 {ticket_id} 用户说：{user_text}。输出 JSON。\n{format_instructions}",
            )
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    llm = build_chat_model(
        responses=[
            json.dumps(
                {
                    "ticket_id": "TK-200",
                    "sentiment": "negative",
                    "summary": "客户投诉物流延迟",
                },
                ensure_ascii=False,
            )
        ]
    )
    return prompt | llm | parser


def build_parallel_chain():
    """RunnableParallel：一次输入，多路变换。"""
    enrich = RunnableParallel(
        question=RunnablePassthrough(),
        length=RunnableLambda(lambda x: len(str(x))),
        upper=RunnableLambda(lambda x: str(x).upper()),
    )
    return enrich


def demo_lcel() -> None:
    """命令行演示。"""
    print("=== 简单 LCEL 链 ===")
    chain = build_simple_lcel_chain()
    print(chain.invoke({"question": "LangChain 是什么？"}))
    print(f"mock={is_mock_mode()}")
    print()

    print("=== JSON OutputParser ===")
    json_chain = build_json_chain()
    data = json_chain.invoke({"ticket_id": "TK-100"})
    print(data)
    assert isinstance(data, dict)
    print()

    print("=== Pydantic OutputParser ===")
    pydantic_chain = build_pydantic_chain()
    summary = pydantic_chain.invoke(
        {"ticket_id": "TK-200", "user_text": "快递太慢了"}
    )
    print(summary)
    print()

    print("=== RunnableParallel ===")
    parallel = build_parallel_chain()
    result = parallel.invoke("星火智服")
    print(result)


if __name__ == "__main__":
    demo_lcel()
