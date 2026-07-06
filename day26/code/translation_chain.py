# -*- coding: utf-8 -*-
"""Day 26 · 翻译 LCEL 链 —— 星火智服产品文案多语言。"""

from __future__ import annotations

import sys
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from mock_llm import build_chat_model  # noqa: E402

# 课堂 mock 预设译文（按调用顺序循环）
_MOCK_TRANSLATIONS = {
    ("星火智服智能客服平台", "英文"): "SparkTech Intelligent Customer Service Platform",
    ("星火智服智能客服平台", "日文"): "星火智服スマートカスタマーサービスプラットフォーム",
    ("7×24 小时在线支持", "英文"): "7×24 online support",
}


def _mock_translate(inputs: dict) -> str:
    """mock 模式：查表或模板化返回，避免依赖 Fake 列表顺序。"""
    text = inputs["source_text"]
    lang = inputs["target_language"]
    key = (text, lang)
    if key in _MOCK_TRANSLATIONS:
        return _MOCK_TRANSLATIONS[key]
    return f"[mock翻译→{lang}] {text}"


def build_translation_chain(*, use_mock_logic: bool = True):
    """
    构建翻译链：

    RunnablePassthrough.assign(...) | prompt | llm | StrOutputParser

    assign 步骤把 source_text / target_language 整理进 dict。
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是星火智服的专业翻译。只输出译文，不要解释。",
            ),
            (
                "human",
                "将以下{source_lang}文本翻译为{target_language}：\n{source_text}",
            ),
        ]
    )

    prepare = RunnablePassthrough.assign(
        source_lang=lambda x: x.get("source_lang", "中文"),
    )

    llm = build_chat_model(
        responses=[
            "SparkTech Intelligent Customer Service Platform",
            "7×24 online support",
            "星火智服スマートカスタマーサービスプラットフォーム",
        ]
    )

    if use_mock_logic:
        # mock：用确定性函数替代 LLM，便于课堂演示与测试
        translate = RunnableLambda(_mock_translate)
        return prepare | translate

    return prepare | prompt | llm | StrOutputParser()


def translate(
    source_text: str,
    target_language: str = "英文",
    *,
    source_lang: str = "中文",
) -> str:
    """翻译便捷入口。"""
    chain = build_translation_chain()
    return chain.invoke(
        {
            "source_text": source_text,
            "target_language": target_language,
            "source_lang": source_lang,
        }
    )


def demo_translation() -> None:
    samples = [
        ("星火智服智能客服平台", "英文"),
        ("7×24 小时在线支持", "英文"),
        ("星火智服智能客服平台", "日文"),
    ]
    print("=== 星火智服翻译链 LCEL ===\n")
    for text, lang in samples:
        result = translate(text, lang)
        print(f"[{lang}] {text}")
        print(f"  → {result}\n")


if __name__ == "__main__":
    demo_translation()
