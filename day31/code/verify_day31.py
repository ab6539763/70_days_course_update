# -*- coding: utf-8 -*-
"""Day 31 验收脚本 —— 无 API Key 时全部 mock 通过。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ.setdefault("SPARKTECH_MOCK", "1")

from rag_common import (  # noqa: E402
    chunk_text,
    cosine_similarity,
    hit_at_k,
    load_corpus,
    mock_embed_text,
    reciprocal_rank_fusion,
    split_by_headings,
)
from rag_tuning_lab import (  # noqa: E402
    EVAL_QUERIES,
    build_chunks,
    evaluate_config,
    run_grid_search,
    vector_search,
)


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_corpus() -> None:
    text = load_corpus()
    if len(text) < 200:
        fail("语料过短")
    sections = split_by_headings(text)
    if len(sections) < 5:
        fail(f"章节过少: {len(sections)}")
    ok(f"语料 {len(text)} 字符, {len(sections)} 章节")


def test_chunk_text() -> None:
    chunks = chunk_text("a" * 1000, chunk_size=300, overlap=50)
    if len(chunks) < 3:
        fail("切块数量异常")
    ok("chunk_text 固定窗口")


def test_mock_embedding() -> None:
    v1 = mock_embed_text("退款政策", model="mock-a")
    v2 = mock_embed_text("退款政策", model="mock-a")
    v3 = mock_embed_text("退款政策", model="mock-b")
    if v1 != v2:
        fail("同模型同文本应一致")
    if v1 == v3:
        fail("不同模型应产生不同向量")
    sim = cosine_similarity(v1, v2)
    if sim < 0.99:
        fail(f"相同向量相似度应≈1: {sim}")
    ok("mock embedding 确定性")


def test_langchain_splitter() -> None:
    corpus = load_corpus()
    for size in (256, 512):
        docs = build_chunks(corpus, size)
        if not docs:
            fail(f"chunk_size={size} 无文档")
    ok("RecursiveCharacterTextSplitter")


def test_vector_search() -> None:
    corpus = load_corpus()
    docs = build_chunks(corpus, 256)
    top_k = 3
    results = vector_search("如何退款", docs, "text-embedding-3-small", top_k=top_k)
    if not results:
        fail("vector_search 无结果")
    if len(results) > top_k:
        fail(f"结果数不应超过 top_k: {len(results)}")
    blob = " ".join(d.page_content.lower() for d, _ in results)
    if "退款" not in blob and "refund" not in blob:
        fail(f"退款查询未命中相关块: {blob[:80]}")
    ok(f"vector_search 退款查询 ({len(results)} 条)")


def test_evaluate_config() -> None:
    corpus = load_corpus()
    r = evaluate_config(corpus, chunk_size=512, top_k=5, embedding_model="bge-small-zh-v1.5")
    if r.hit_rate <= 0:
        fail(f"hit_rate 应 > 0: {r}")
    if r.latency_ms <= 0:
        fail("latency 应 > 0")
    ok(f"evaluate_config hit_rate={r.hit_rate}")


def test_grid_search() -> None:
    corpus = load_corpus()
    # 缩小网格加速验收
    import rag_tuning_lab as lab

    orig_models = lab.EMBEDDING_MODELS
    orig_chunks = lab.CHUNK_SIZES
    orig_topk = lab.TOP_K_VALUES
    try:
        lab.EMBEDDING_MODELS = ["text-embedding-3-small"]
        lab.CHUNK_SIZES = [512]
        lab.TOP_K_VALUES = [3, 5]
        results = run_grid_search(corpus)
    finally:
        lab.EMBEDDING_MODELS = orig_models
        lab.CHUNK_SIZES = orig_chunks
        lab.TOP_K_VALUES = orig_topk
    if len(results) != 2:
        fail(f"缩小网格应 2 组结果: {len(results)}")
    ok("run_grid_search 缩小网格")


def test_rrf() -> None:
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["b", "a", "d"]], top_n=3)
    ids = [x[0] for x in fused]
    if "a" not in ids or "b" not in ids:
        fail(f"RRF 应融合 a,b: {ids}")
    ok("reciprocal_rank_fusion")


def test_quiz_file() -> None:
    quiz = CODE_DIR / "week4_review_quiz.md"
    if not quiz.is_file():
        fail("week4_review_quiz.md 缺失")
    content = quiz.read_text(encoding="utf-8")
    if "RAG" not in content:
        fail("测验应含 RAG 题目")
    ok("week4_review_quiz.md")


def test_eval_queries() -> None:
    if len(EVAL_QUERIES) < 5:
        fail("评测查询过少")
    ok(f"EVAL_QUERIES {len(EVAL_QUERIES)} 条")


def main() -> None:
    print("=== Day 31 verify ===\n")
    test_corpus()
    test_chunk_text()
    test_mock_embedding()
    test_langchain_splitter()
    test_vector_search()
    test_evaluate_config()
    test_grid_search()
    test_rrf()
    test_quiz_file()
    test_eval_queries()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
