# -*- coding: utf-8 -*-
"""
Day 33 · Rerank 演示：bge-reranker 或 mock 交叉编码器重排
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from hybrid_retriever import HybridRetriever, build_child_docs
from rag_common import load_corpus, tokenize_zh


@dataclass
class RankedDoc:
    query: str
    content: str
    score: float
    source: str


def mock_cross_encoder_score(query: str, document: str) -> float:
    """
    mock 重排：关键词重叠 + 长度惩罚。
    模拟 cross-encoder 对 (query, doc) 联合打分。
    """
    q_tokens = set(tokenize_zh(query))
    d_tokens = set(tokenize_zh(document))
    if not q_tokens:
        return 0.0
    overlap = len(q_tokens & d_tokens) / len(q_tokens)
    # 奖励包含完整英文词（如 API、P0）
    for term in re.findall(r"[a-z0-9]+", query.lower()):
        if term in document.lower():
            overlap += 0.15
    overlap = min(overlap, 1.0)
    # 轻度长度惩罚
    len_penalty = min(len(document) / 2000, 0.2)
    return round(overlap - len_penalty, 4)


class MockBGEReranker:
    """mock bge-reranker-base；live 可换 sentence-transformers CrossEncoder。"""

    def __init__(self, model_name: str = "BAAI/bge-reranker-base") -> None:
        self.model_name = model_name
        self._live_model = None

    def _try_load_live(self) -> bool:
        try:
            from sentence_transformers import CrossEncoder  # type: ignore
        except ImportError:
            return False
        import os

        if os.getenv("SPARKTECH_MOCK", "1").strip().lower() not in {"0", "false", "no"}:
            return False
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("HF_TOKEN"):
            return False
        try:
            self._live_model = CrossEncoder(self.model_name)
            return True
        except Exception:
            return False

    def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
        if self._live_model is not None or self._try_load_live():
            assert self._live_model is not None
            return [float(s) for s in self._live_model.predict(pairs)]
        return [mock_cross_encoder_score(q, d) for q, d in pairs]


def rerank(query: str, candidates: list[str], top_n: int = 3) -> list[RankedDoc]:
    reranker = MockBGEReranker()
    pairs = [(query, c) for c in candidates]
    scores = reranker.score_pairs(pairs)
    ranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True,
    )[:top_n]
    return [
        RankedDoc(query=query, content=doc, score=score, source="mock-rerank")
        for doc, score in ranked
    ]


def main() -> None:
    corpus = load_corpus()
    docs = build_child_docs(corpus)
    hybrid = HybridRetriever(docs)
    query = "退款到账需要几天"
    hits = hybrid.retrieve(query, top_k=6)
    candidates = [h.content for h in hits]
    print("Day 33 · rerank_demo")
    print(f"Query: {query}\n")
    print("Hybrid 候选（RRF 序）:")
    for i, c in enumerate(candidates[:4], 1):
        print(f"  [{i}] {c[:60]}...")
    print("\nRerank 后:")
    for i, r in enumerate(rerank(query, candidates, top_n=3), 1):
        print(f"  [{i}] score={r.score:.4f} | {r.content[:60]}...")


if __name__ == "__main__":
    main()
