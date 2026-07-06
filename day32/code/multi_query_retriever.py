# -*- coding: utf-8 -*-
"""
Day 32 · Multi-Query Retriever

从一个用户问题生成多条检索查询，合并去重后返回文档。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_common import cosine_similarity, load_corpus, mock_embed_text
from query_rewrite_demo import mock_rewrite


@dataclass
class MultiQueryResult:
    original_query: str
    sub_queries: list[str] = field(default_factory=list)
    merged_docs: list[Document] = field(default_factory=list)
    scores: list[float] = field(default_factory=list)


def generate_sub_queries(query: str, n: int = 3) -> list[str]:
    """mock：原句 + 改写 + 关键词扩展。"""
    base = mock_rewrite(query)
    variants = [query, base]
    # 简单关键词扩展
    if "退款" in base or "退" in query:
        variants.append("退款政策 到账时间")
    if "api" in query.lower() or "key" in query.lower():
        variants.append("API Key 申请 审批")
    if "企业" in query or "定价" in base:
        variants.append("企业版 订阅 价格")
    if "故障" in base or "挂" in query:
        variants.append("工单 SLA P0 响应")
    # 去重保序
    seen: set[str] = set()
    out: list[str] = []
    for v in variants:
        v = v.strip()
        if v and v not in seen:
            seen.add(v)
            out.append(v)
        if len(out) >= n:
            break
    while len(out) < n:
        out.append(base)
    return out[:n]


class MultiQueryRetriever:
    def __init__(self, docs: list[Document], top_k_per_query: int = 3) -> None:
        self.docs = docs
        self.top_k_per_query = top_k_per_query

    def _search_one(self, query: str, top_k: int) -> list[tuple[Document, float]]:
        q_vec = mock_embed_text(query, model="mock-multi")
        scored = []
        for doc in self.docs:
            d_vec = mock_embed_text(doc.page_content, model="mock-multi")
            scored.append((doc, cosine_similarity(q_vec, d_vec)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def retrieve(self, query: str, final_k: int = 5) -> MultiQueryResult:
        sub_queries = generate_sub_queries(query)
        merged: dict[str, tuple[Document, float]] = {}
        for sq in sub_queries:
            for doc, score in self._search_one(sq, self.top_k_per_query):
                key = doc.page_content[:80]
                if key not in merged or score > merged[key][1]:
                    merged[key] = (doc, score)
        ranked = sorted(merged.values(), key=lambda x: x[1], reverse=True)[:final_k]
        return MultiQueryResult(
            original_query=query,
            sub_queries=sub_queries,
            merged_docs=[d for d, _ in ranked],
            scores=[s for _, s in ranked],
        )


def build_docs(corpus: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    return splitter.create_documents([corpus])


def main() -> None:
    corpus = load_corpus()
    docs = build_docs(corpus)
    retriever = MultiQueryRetriever(docs, top_k_per_query=3)
    queries = ["能退钱吗", "API key 咋弄", "P0 故障响应时间"]
    print("Day 32 · multi_query_retriever\n")
    for q in queries:
        result = retriever.retrieve(q, final_k=4)
        print(f"原问: {result.original_query}")
        print(f"子查询: {result.sub_queries}")
        for i, doc in enumerate(result.merged_docs[:2], 1):
            preview = doc.page_content.replace("\n", " ")[:60]
            print(f"  [{i}] score={result.scores[i-1]:.4f} {preview}...")
        print()


if __name__ == "__main__":
    main()
