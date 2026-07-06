# -*- coding: utf-8 -*-
"""Day 32 验收脚本 —— 无 API Key 时全部 mock 通过。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ.setdefault("SPARKTECH_MOCK", "1")

from hyde_demo import HyDERetriever, build_docs, compress_context, mock_hyde_document  # noqa: E402
from multi_query_retriever import MultiQueryRetriever, generate_sub_queries  # noqa: E402
from query_rewrite_demo import compare_rewrite, mock_rewrite  # noqa: E402
from rag_common import load_corpus  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_mock_rewrite() -> None:
    r = mock_rewrite("咋申请 key")
    if "API" not in r and "Key" not in r and "key" not in r.lower():
        fail(f"改写应含 Key: {r}")
    ok(f"mock_rewrite -> {r}")


def test_compare_rewrite() -> None:
    corpus = load_corpus()
    docs = build_docs(corpus)
    result = compare_rewrite("能退钱不", docs)
    if not result.rewritten:
        fail("改写结果为空")
    ok("compare_rewrite")


def test_multi_query() -> None:
    subs = generate_sub_queries("能退钱吗", n=3)
    if len(subs) < 2:
        fail(f"子查询过少: {subs}")
    corpus = load_corpus()
    docs = build_docs(corpus)
    mq = MultiQueryRetriever(docs).retrieve("API key 咋弄", final_k=3)
    if not mq.merged_docs:
        fail("multi query 无结果")
    ok(f"multi_query {len(mq.sub_queries)} 子查询 -> {len(mq.merged_docs)} 文档")


def test_hyde() -> None:
    hypo = mock_hyde_document("退款多久到账")
    if "退款" not in hypo:
        fail(f"HyDE 假设文档异常: {hypo}")
    corpus = load_corpus()
    docs = build_docs(corpus)
    result = HyDERetriever(docs).retrieve("API Key 申请", top_k=2)
    if not result.hits:
        fail("HyDE 无命中")
    ok("HyDERetriever")


def test_compress() -> None:
    corpus = load_corpus()
    docs = build_docs(corpus)
    compressed = compress_context(docs[:5], max_chars=400)
    if len(compressed) > 450:
        fail(f"压缩超长: {len(compressed)}")
    if len(compressed) < 50:
        fail("压缩过短")
    ok(f"compress_context {len(compressed)} chars")


def main() -> None:
    print("=== Day 32 verify ===\n")
    test_mock_rewrite()
    test_compare_rewrite()
    test_multi_query()
    test_hyde()
    test_compress()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
