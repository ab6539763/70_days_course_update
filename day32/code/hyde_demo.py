# -*- coding: utf-8 -*-
"""
Day 32 · HyDE (Hypothetical Document Embeddings)

用 LLM 生成「假设性答案文档」，对其 embedding 做检索。
mock 模式用模板生成假设文档。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_common import cosine_similarity, is_mock_mode, load_corpus, mock_embed_text

HYDE_PROMPT = """根据问题写一段可能出现在知识库中的答案（80字内，不要寒暄）。
问题：{query}
答案："""


@dataclass
class HyDEResult:
    query: str
    hypothetical_doc: str
    hits: list[tuple[str, float]]


def mock_hyde_document(query: str) -> str:
    """模板生成假设文档。"""
    q = query.lower()
    if "退款" in q or "退钱" in q:
        return (
            "用户可在订单完成后7天内申请无理由退款。退款原路返回，"
            "到账通常需要3-5个工作日。虚拟商品激活后可能不可退。"
        )
    if "api" in q or "key" in q or "密钥" in q:
        return (
            "API Key 在星火控制台开发者密钥管理中申请，提交后管理员审批，"
            "通常1个工作日内生效。请勿在客户端硬编码 Key。"
        )
    if "企业" in q or "定价" in q or "价格" in q:
        return "企业版按年订阅，标准价12万年起，含专属客服与SLA 99.9%。"
    if "rag" in q or "切块" in q or "chunk" in q:
        return "RAG文档切块建议300-800字符，重叠50-100。检索top_k通常3-5。"
    if "p0" in q or "故障" in q or "响应" in q:
        return "P0故障15分钟响应、4小时恢复；P1问题2小时响应。"
    return f"关于「{query}」的说明：请参阅星火智服内部知识库相关章节。"


def generate_hypothetical_document(query: str) -> str:
    if is_mock_mode():
        return mock_hyde_document(query)

    try:
        from openai import OpenAI
    except ImportError:
        return mock_hyde_document(query)

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": HYDE_PROMPT.format(query=query)}],
        temperature=0.3,
        max_tokens=150,
    )
    return (resp.choices[0].message.content or "").strip() or mock_hyde_document(query)


class HyDERetriever:
    def __init__(self, docs: list[Document]) -> None:
        self.docs = docs

    def retrieve(self, query: str, top_k: int = 3) -> HyDEResult:
        hypo = generate_hypothetical_document(query)
        h_vec = mock_embed_text(hypo, model="mock-hyde")
        scored: list[tuple[str, float]] = []
        for doc in self.docs:
            d_vec = mock_embed_text(doc.page_content, model="mock-hyde")
            scored.append((doc.page_content[:100], cosine_similarity(h_vec, d_vec)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return HyDEResult(query=query, hypothetical_doc=hypo, hits=scored[:top_k])


def build_docs(corpus: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    return splitter.create_documents([corpus])


def compress_context(docs: list[Document], max_chars: int = 600) -> str:
    """上下文压缩：按分数顺序拼接直到字符上限。"""
    parts: list[str] = []
    total = 0
    for doc in docs:
        text = doc.page_content.strip()
        if total + len(text) > max_chars:
            remain = max_chars - total
            if remain > 50:
                parts.append(text[:remain] + "...")
            break
        parts.append(text)
        total += len(text)
    return "\n---\n".join(parts)


def main() -> None:
    corpus = load_corpus()
    docs = build_docs(corpus)
    retriever = HyDERetriever(docs)
    queries = ["能退钱吗", "API Key 申请流程", "RAG 切块多大"]
    print("Day 32 · hyde_demo")
    print(f"模式: {'mock' if is_mock_mode() else 'live'}\n")
    for q in queries:
        result = retriever.retrieve(q, top_k=2)
        print(f"Q: {result.query}")
        print(f"假设文档: {result.hypothetical_doc}")
        for i, (preview, score) in enumerate(result.hits, 1):
            print(f"  hit[{i}] score={score:.4f} | {preview}...")
        print()


if __name__ == "__main__":
    main()
