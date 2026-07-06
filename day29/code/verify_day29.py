# -*- coding: utf-8 -*-
"""
Day 29 验收脚本 —— 无 API Key 时 mock embedding 全绿。

运行：cd day29/code && python3 verify_day29.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ.setdefault("SPARKTECH_MOCK", "1")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_mock_embeddings() -> None:
    import numpy as np
    from mock_embeddings import SparkMockEmbeddings, get_embeddings, is_mock_mode

    assert is_mock_mode()
    emb = get_embeddings(force_mock=True)
    assert isinstance(emb, SparkMockEmbeddings)
    v1 = emb.embed_query("如何退款")
    v2 = emb.embed_query("退款流程")
    v3 = emb.embed_query("天气真好")
    assert len(v1) == len(v2) == 64
    sim_refund = float(np.dot(v1, v2))
    sim_weather = float(np.dot(v1, v3))
    assert sim_refund > sim_weather, f"退款相关应更相似: {sim_refund} vs {sim_weather}"
    ok(f"mock embeddings sim_refund={sim_refund:.4f} > sim_weather={sim_weather:.4f}")


def test_chroma_kb() -> None:
    from langchain_core.documents import Document

    from chroma_kb import ChromaKnowledgeBase

    kb = ChromaKnowledgeBase()
    kb.reset()
    docs = [
        Document(page_content="退款在工单系统申请，三个工作日审核。", metadata={"source": "faq.txt"}),
        Document(page_content="在线客服工作日九点到十八点响应。", metadata={"source": "policy.txt"}),
    ]
    kb.add_documents(docs)
    assert kb.count() >= 2
    hits = kb.similarity_search_with_score("怎么退钱", k=1)
    assert hits, "应有检索结果"
    assert "退款" in hits[0].content or "工单" in hits[0].content
    retriever = kb.as_retriever(search_kwargs={"k": 1})
    retrieved = retriever.invoke("退款")
    assert len(retrieved) >= 1
    ok("ChromaKnowledgeBase add/search/retriever")


def test_build_vectorstore() -> None:
    from build_vectorstore import build_vectorstore, resolve_docs_dir

    docs_dir = resolve_docs_dir()
    assert docs_dir.is_dir(), f"sample_docs 缺失: {docs_dir}"
    kb, report = build_vectorstore(reset=True)
    assert report.chunks >= 5, f"切块过少: {report.chunks}"
    assert kb.count() >= 5, f"向量库条数过少: {kb.count()}"
    ok(f"build_vectorstore chunks={report.chunks} count={kb.count()}")


def test_similarity_demo() -> None:
    from build_vectorstore import build_vectorstore
    from similarity_search_demo import run_demo

    kb, _ = build_vectorstore(reset=True)
    results = run_demo(kb=kb)
    assert len(results) >= 6
    refund_hits = results[0].hits
    assert refund_hits, "退款 query 应有命中"
    ok("similarity_search_demo queries")


def main() -> None:
    print("=== Day 29 verify ===\n")
    test_mock_embeddings()
    test_chroma_kb()
    test_build_vectorstore()
    test_similarity_demo()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
