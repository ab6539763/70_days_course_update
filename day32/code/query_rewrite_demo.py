# -*- coding: utf-8 -*-
"""
Day 32 · 查询改写演示

将口语化/模糊问句改写为更适合检索的形式。
mock 模式使用规则模板；live 模式调用 LLM。
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_common import cosine_similarity, is_mock_mode, load_corpus, mock_embed_text

REWRITE_PROMPT = """你是检索查询优化助手。将用户问题改写为适合知识库检索的简洁问句。
要求：保留核心意图；补充缺失实体；输出一行 JSON：{{"rewritten": "..."}}

用户问题：{query}
"""


@dataclass
class RewriteResult:
    original: str
    rewritten: str
    mode: str
    retrieval_gain: float = 0.0


def mock_rewrite(query: str) -> str:
    """规则改写：口语 → 标准问法。"""
    q = query.strip()
    rules: list[tuple[str, str]] = [
        (r"咋|怎么|如何", "如何"),
        (r"退钱|能退吗|不想要了", "退款"),
        (r"key|密钥|口令", "API Key"),
        (r"多少钱|啥价|价格", "定价"),
        (r"多久|多长时间", "需要多长时间"),
        (r"坏了|挂了|不能用", "故障"),
    ]
    out = q
    for pattern, repl in rules:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    if "？" not in out and "?" not in out:
        out = out.rstrip("。") + "？"
    return out


def llm_rewrite(query: str) -> str:
    if is_mock_mode():
        return mock_rewrite(query)

    try:
        from openai import OpenAI
    except ImportError:
        return mock_rewrite(query)

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = REWRITE_PROMPT.format(query=query)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    text = resp.choices[0].message.content or ""
    try:
        data = json.loads(text.strip())
        return str(data.get("rewritten", text))
    except json.JSONDecodeError:
        return text.strip() or mock_rewrite(query)


def build_index(corpus: str, chunk_size: int = 512) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=64)
    return splitter.create_documents([corpus])


def search(query: str, docs: list[Document], top_k: int = 3) -> list[tuple[Document, float]]:
    q_vec = mock_embed_text(query, model="mock-rewrite")
    scored = []
    for doc in docs:
        d_vec = mock_embed_text(doc.page_content, model="mock-rewrite")
        scored.append((doc, cosine_similarity(q_vec, d_vec)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def compare_rewrite(query: str, docs: list[Document]) -> RewriteResult:
    rewritten = llm_rewrite(query)
    before = search(query, docs, top_k=3)
    after = search(rewritten, docs, top_k=3)
    gain = 0.0
    if after and before:
        gain = after[0][1] - before[0][1]
    return RewriteResult(
        original=query,
        rewritten=rewritten,
        mode="mock" if is_mock_mode() else "live",
        retrieval_gain=round(gain, 4),
    )


DEMO_QUERIES = [
    "咋申请那个 key 啊",
    "能退钱不",
    "企业版啥价",
    "系统挂了多久有人管",
]


def main() -> None:
    corpus = load_corpus()
    docs = build_index(corpus)
    print("Day 32 · query_rewrite_demo")
    print(f"模式: {'mock' if is_mock_mode() else 'live'}\n")
    print(f"{'原问句':<24} {'改写后':<28} {'gain':>8}")
    print("-" * 64)
    for q in DEMO_QUERIES:
        r = compare_rewrite(q, docs)
        print(f"{r.original:<24} {r.rewritten:<28} {r.retrieval_gain:>8.4f}")


if __name__ == "__main__":
    main()
