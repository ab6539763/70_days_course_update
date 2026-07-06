# -*- coding: utf-8 -*-
"""Day 33 验收脚本 —— 无 API Key 时全部 mock 通过。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ.setdefault("SPARKTECH_MOCK", "1")

from enhanced_rag_pipeline import (  # noqa: E402
    EnhancedRAGPipeline,
    build_parent_child_index,
    compress_context,
)
from hybrid_retriever import HybridRetriever, build_child_docs  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from rag_common import load_corpus, reciprocal_rank_fusion  # noqa: E402
from rerank_demo import MockBGEReranker, mock_cross_encoder_score, rerank  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_bm25_vector() -> None:
    corpus = load_corpus()
    docs = build_child_docs(corpus)
    hr = HybridRetriever(docs)
    bm = hr.bm25_search("退款", top_k=3)
    vec = hr.vector_search("退款", top_k=3)
    if not bm or not vec:
        fail("BM25 或向量检索无结果")
    ok(f"BM25 top={bm[0][0]} | Vector top={vec[0][0]}")


def test_rrf_hybrid() -> None:
    corpus = load_corpus()
    docs = build_child_docs(corpus)
    hits = HybridRetriever(docs).retrieve("API Key 申请", top_k=3)
    if len(hits) < 1:
        fail("hybrid 无结果")
    blob = " ".join(h.content for h in hits).lower()
    if "api" not in blob and "key" not in blob and "密钥" not in blob:
        fail(f"API 查询未命中: {blob[:80]}")
    ok(f"hybrid RRF {len(hits)} hits")


def test_rerank() -> None:
    cands = ["退款原路返回3-5个工作日", "企业版定价12万", "API Key 审批1天"]
    ranked = rerank("退款到账", cands, top_n=2)
    if "退款" not in ranked[0].content:
        fail(f"rerank 首条应含退款: {ranked[0].content}")
    score = mock_cross_encoder_score("退款", "退款政策")
    if score <= 0:
        fail("cross encoder mock 分数应 > 0")
    ok(f"rerank top score={ranked[0].score}")


def test_parent_index() -> None:
    corpus = load_corpus()
    idx = build_parent_child_index(corpus)
    if len(idx.parents) < 5:
        fail(f"父文档过少: {len(idx.parents)}")
    if len(idx.children) < len(idx.parents):
        fail("子块应不少于父文档数")
    ok(f"parent-child {len(idx.parents)} parents, {len(idx.children)} children")


def test_pipeline() -> None:
    corpus = load_corpus()
    idx = build_parent_child_index(corpus)
    result = EnhancedRAGPipeline(idx).run("能退钱吗")
    if not result.answer:
        fail("pipeline 无回答")
    if not result.parent_docs:
        fail("pipeline 未解析父文档")
    ok(f"pipeline answer len={len(result.answer)}")


def test_compress() -> None:
    docs = [Document(page_content="a" * 300) for _ in range(5)]
    c = compress_context(docs, max_chars=500)
    if len(c) > 550:
        fail(f"压缩失败: {len(c)}")
    ok("compress_context")


def test_rrf_util() -> None:
    fused = reciprocal_rank_fusion([["x", "y"], ["y", "z"]], top_n=2)
    if fused[0][0] != "y":
        fail(f"RRF 应优先 y: {fused}")
    ok("RRF fusion")


def main() -> None:
    print("=== Day 33 verify ===\n")
    test_bm25_vector()
    test_rrf_hybrid()
    test_rerank()
    test_parent_index()
    test_pipeline()
    test_compress()
    test_rrf_util()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
