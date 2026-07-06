# -*- coding: utf-8 -*-
"""
Day 33 · 增强 RAG 管道

串联：Parent Document → Hybrid(BM25+Vector+RRF) → Rerank → Context Compress → Mock 生成
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from hybrid_retriever import HybridRetriever
from rag_common import is_mock_mode, load_corpus, split_by_headings
from rerank_demo import rerank


def mock_rewrite(query: str) -> str:
    q = query.strip()
    rules = [
        (r"咋|怎么|如何", "如何"),
        (r"退钱|能退吗", "退款"),
        (r"key|密钥", "API Key"),
        (r"多久|多长时间", "需要多长时间"),
        (r"故障|挂了", "故障"),
    ]
    out = q
    for pattern, repl in rules:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def compress_context(docs: list[Document], max_chars: int = 800) -> str:
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


@dataclass
class ParentChildIndex:
    parents: list[Document]
    children: list[Document]
    child_to_parent_id: dict[str, str]


def build_parent_child_index(corpus: str) -> ParentChildIndex:
    """父文档 = ## 章节；子块 = 较小 chunk 带 parent_id metadata。"""
    sections = split_by_headings(corpus)
    parents: list[Document] = []
    children: list[Document] = []
    child_to_parent: dict[str, str] = {}

    splitter = RecursiveCharacterTextSplitter(chunk_size=180, chunk_overlap=30)

    for i, sec in enumerate(sections):
        parent_id = f"parent-{i}"
        parent_doc = Document(
            page_content=f"## {sec['title']}\n{sec['content']}",
            metadata={"parent_id": parent_id, "title": sec["title"]},
        )
        parents.append(parent_doc)
        for j, chunk in enumerate(splitter.split_text(sec["content"])):
            child_id = f"{parent_id}-child-{j}"
            child = Document(
                page_content=chunk,
                metadata={"parent_id": parent_id, "title": sec["title"], "child_id": child_id},
            )
            children.append(child)
            child_to_parent[child_id] = parent_id

    return ParentChildIndex(parents=parents, children=children, child_to_parent_id=child_to_parent)


@dataclass
class PipelineResult:
    query: str
    rewritten_query: str
    child_hits: list[str] = field(default_factory=list)
    parent_docs: list[str] = field(default_factory=list)
    reranked: list[str] = field(default_factory=list)
    context: str = ""
    answer: str = ""


class EnhancedRAGPipeline:
    def __init__(self, index: ParentChildIndex) -> None:
        self.index = index
        child_ids = [c.metadata.get("child_id", f"c-{i}") for i, c in enumerate(index.children)]
        self.hybrid = HybridRetriever(index.children, doc_ids=child_ids)
        self.parent_map = {p.metadata["parent_id"]: p for p in index.parents}

    def _resolve_parents(self, child_hits: list[Document]) -> list[Document]:
        seen: set[str] = set()
        parents: list[Document] = []
        for child in child_hits:
            pid = child.metadata.get("parent_id", "")
            if pid and pid not in seen and pid in self.parent_map:
                seen.add(pid)
                parents.append(self.parent_map[pid])
        return parents

    def _generate(self, query: str, context: str) -> str:
        if is_mock_mode():
            snippet = context[:120].replace("\n", " ")
            return f"[mock 回答] 根据知识库：{snippet}（问题：{query}）"
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            prompt = (
                f"根据资料回答问题，资料未提及则说「资料中未提及」。\n\n"
                f"资料：\n{context}\n\n问题：{query}"
            )
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception:
            snippet = context[:120].replace("\n", " ")
            return f"[mock 回答] 根据知识库：{snippet}（问题：{query}）"

    def run(self, query: str, top_k: int = 5) -> PipelineResult:
        rewritten = mock_rewrite(query)
        hybrid_hits = self.hybrid.retrieve(rewritten, top_k=top_k)
        child_docs = [
            Document(page_content=h.content, metadata=h.metadata) for h in hybrid_hits
        ]
        parent_docs = self._resolve_parents(child_docs)
        reranked = rerank(rewritten, [p.page_content for p in parent_docs], top_n=3)
        context = compress_context(
            [Document(page_content=r.content) for r in reranked],
            max_chars=800,
        )
        answer = self._generate(rewritten, context)
        return PipelineResult(
            query=query,
            rewritten_query=rewritten,
            child_hits=[c.page_content[:80] for c in child_docs[:3]],
            parent_docs=[p.metadata.get("title", "") for p in parent_docs],
            reranked=[r.content[:80] for r in reranked],
            context=context[:200] + ("..." if len(context) > 200 else ""),
            answer=answer,
        )


def main() -> None:
    corpus = load_corpus()
    index = build_parent_child_index(corpus)
    pipeline = EnhancedRAGPipeline(index)
    queries = ["能退钱吗多久到账", "API Key 审批要多久", "P0 故障响应时间"]
    print("Day 33 · enhanced_rag_pipeline")
    print(f"模式: {'mock' if is_mock_mode() else 'live'}")
    print(f"父文档: {len(index.parents)} | 子块: {len(index.children)}\n")
    for q in queries:
        result = pipeline.run(q)
        print(f"Q: {result.query}")
        print(f"改写: {result.rewritten_query}")
        print(f"父文档: {result.parent_docs}")
        print(f"回答: {result.answer[:120]}...")
        print("-" * 60)


if __name__ == "__main__":
    main()
