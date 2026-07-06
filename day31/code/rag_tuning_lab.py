# -*- coding: utf-8 -*-
"""
Day 31 · RAG 调参实验台

实验维度：
1. chunk_size（256 / 512 / 1024）
2. top_k（3 / 5 / 10）
3. embedding 模型对比（mock 三种「模型」）

运行：python3 rag_tuning_lab.py
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_common import (
    cosine_similarity,
    get_langchain_embeddings,
    hit_at_k,
    is_mock_mode,
    load_corpus,
    mock_embed_text,
)

CODE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = CODE_DIR / "output"

# 评测查询：query -> 期望命中的关键词
EVAL_QUERIES: list[dict[str, Any]] = [
    {"query": "怎么申请 API Key？", "keywords": ["api key", "密钥", "申请"]},
    {"query": "退款要几天到账？", "keywords": ["退款", "到账", "工作日"]},
    {"query": "企业版多少钱？", "keywords": ["企业版", "定价", "万"]},
    {"query": "RAG 切块多大合适？", "keywords": ["切块", "chunk", "top_k"]},
    {"query": "P0 故障多久响应？", "keywords": ["p0", "15", "响应"]},
]

CHUNK_SIZES = [256, 512, 1024]
TOP_K_VALUES = [3, 5, 10]
EMBEDDING_MODELS = [
    "text-embedding-3-small",
    "bge-small-zh-v1.5",
    "multilingual-e5-small",
]


@dataclass
class RetrievalHit:
    query: str
    chunk: str
    score: float


@dataclass
class ExperimentResult:
    chunk_size: int
    top_k: int
    embedding_model: str
    hit_rate: float
    avg_top_score: float
    latency_ms: float
    hits: list[RetrievalHit] = field(default_factory=list)


def build_chunks(corpus: str, chunk_size: int, overlap: int | None = None) -> list[Document]:
    overlap = overlap or max(40, chunk_size // 8)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", "。", "；", " ", ""],
    )
    return splitter.create_documents([corpus])


def vector_search(
    query: str,
    docs: list[Document],
    embeddings_model: str,
    top_k: int,
) -> list[tuple[Document, float]]:
    """纯向量检索（mock / live embedding）。"""
    if is_mock_mode():
        q_vec = mock_embed_text(query, model=f"mock-{embeddings_model}")
        scored: list[tuple[Document, float]] = []
        for doc in docs:
            d_vec = mock_embed_text(doc.page_content, model=f"mock-{embeddings_model}")
            scored.append((doc, cosine_similarity(q_vec, d_vec)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    emb = get_langchain_embeddings(embeddings_model)
    q_vec = emb.embed_query(query)
    scored = []
    for doc in docs:
        d_vec = emb.embed_documents([doc.page_content])[0]
        scored.append((doc, cosine_similarity(q_vec, d_vec)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def evaluate_config(
    corpus: str,
    chunk_size: int,
    top_k: int,
    embedding_model: str,
) -> ExperimentResult:
    t0 = time.perf_counter()
    docs = build_chunks(corpus, chunk_size)
    hits_detail: list[RetrievalHit] = []
    success = 0
    score_sum = 0.0

    for item in EVAL_QUERIES:
        query = item["query"]
        keywords: list[str] = item["keywords"]
        results = vector_search(query, docs, embedding_model, top_k)
        retrieved_texts = [d.page_content for d, _ in results]
        if hit_at_k(retrieved_texts, keywords, k=top_k):
            success += 1
        if results:
            score_sum += results[0][1]
            hits_detail.append(
                RetrievalHit(
                    query=query,
                    chunk=results[0][0].page_content[:120] + "...",
                    score=round(results[0][1], 4),
                )
            )

    latency = (time.perf_counter() - t0) * 1000
    n = len(EVAL_QUERIES)
    return ExperimentResult(
        chunk_size=chunk_size,
        top_k=top_k,
        embedding_model=embedding_model,
        hit_rate=round(success / n, 4) if n else 0.0,
        avg_top_score=round(score_sum / n, 4) if n else 0.0,
        latency_ms=round(latency, 2),
        hits=hits_detail,
    )


def run_grid_search(corpus: str) -> list[ExperimentResult]:
    results: list[ExperimentResult] = []
    for model in EMBEDDING_MODELS:
        for chunk_size in CHUNK_SIZES:
            for top_k in TOP_K_VALUES:
                print(f"[实验] model={model} chunk={chunk_size} top_k={top_k} ...")
                results.append(evaluate_config(corpus, chunk_size, top_k, model))
    return results


def print_report(results: list[ExperimentResult]) -> None:
    print("\n" + "=" * 72)
    print("RAG 调参实验报告")
    print(f"模式: {'mock' if is_mock_mode() else 'live'}")
    print("=" * 72)
    header = f"{'model':<28} {'chunk':>6} {'top_k':>6} {'hit%':>8} {'score':>8} {'ms':>8}"
    print(header)
    print("-" * 72)
    for r in sorted(results, key=lambda x: (-x.hit_rate, -x.avg_top_score)):
        print(
            f"{r.embedding_model:<28} {r.chunk_size:>6} {r.top_k:>6} "
            f"{r.hit_rate * 100:>7.1f}% {r.avg_top_score:>8.4f} {r.latency_ms:>8.1f}"
        )
    best = max(results, key=lambda x: (x.hit_rate, x.avg_top_score))
    print("-" * 72)
    print(
        f"推荐配置: chunk_size={best.chunk_size}, top_k={best.top_k}, "
        f"model={best.embedding_model} (hit={best.hit_rate * 100:.1f}%)"
    )


def save_results(results: list[ExperimentResult]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"rag_tuning_{ts}.json"
    payload = [asdict(r) for r in results]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> None:
    corpus = load_corpus()
    print("Day 31 · rag_tuning_lab")
    print(f"语料长度: {len(corpus)} 字符 | 评测查询: {len(EVAL_QUERIES)} 条")
    results = run_grid_search(corpus)
    print_report(results)
    out = save_results(results)
    print(f"\n结果已保存: {out}")


if __name__ == "__main__":
    main()
