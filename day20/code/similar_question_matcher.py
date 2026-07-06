# -*- coding: utf-8 -*-
"""
Day 20 · 相似问匹配工具

基于 embedding + 余弦相似度，从 FAQ 库中检索最相似的标准问。
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from cosine_similarity import cosine_similarity, top_k_similar
from embedding_demo import EmbeddingClient

DEFAULT_QUESTIONS_FILE = Path(__file__).resolve().parent / "sample_questions.json"
DEFAULT_THRESHOLD = 0.75


@dataclass
class FAQItem:
    id: str
    category: str
    question: str
    answer: str
    vector: list[float] = field(default_factory=list)


@dataclass
class MatchResult:
    query: str
    matched: FAQItem | None
    score: float
    top_k: list[tuple[FAQItem, float]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "score": round(self.score, 4),
            "matched": (
                {
                    "id": self.matched.id,
                    "question": self.matched.question,
                    "answer": self.matched.answer,
                    "category": self.matched.category,
                }
                if self.matched
                else None
            ),
            "top_k": [
                {"id": item.id, "question": item.question, "score": round(s, 4)}
                for item, s in self.top_k
            ],
        }


class SimilarQuestionMatcher:
    """FAQ 相似问匹配器。"""

    def __init__(
        self,
        questions_path: Path | None = None,
        *,
        embedding_client: EmbeddingClient | None = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        self.questions_path = questions_path or DEFAULT_QUESTIONS_FILE
        self.client = embedding_client or EmbeddingClient()
        self.threshold = threshold
        self.faq_items: list[FAQItem] = []
        self._matrix: np.ndarray | None = None

    def load(self) -> None:
        """加载 FAQ 并预计算 embedding 矩阵。"""
        with self.questions_path.open(encoding="utf-8") as fh:
            raw = json.load(fh)

        self.faq_items = []
        texts = [item["question"] for item in raw]
        embeddings = self.client.embed_batch(texts)

        for item, emb in zip(raw, embeddings):
            self.faq_items.append(
                FAQItem(
                    id=item["id"],
                    category=item["category"],
                    question=item["question"],
                    answer=item["answer"],
                    vector=emb.vector,
                )
            )

        self._matrix = np.array([f.vector for f in self.faq_items], dtype=np.float64)
        print(f"[matcher] 已索引 {len(self.faq_items)} 条 FAQ（模式: {self.client.mode}）")

    def match(self, query: str, k: int = 3) -> MatchResult:
        """匹配用户问句，返回最佳命中及 top-k。"""
        if self._matrix is None or not self.faq_items:
            raise RuntimeError("请先调用 load()")

        query = query.strip()
        q_vec = np.array(self.client.embed(query).vector, dtype=np.float64)
        top = top_k_similar(q_vec, self._matrix, k=k)

        top_k_pairs = [(self.faq_items[i], score) for i, score in top]
        best_item, best_score = top_k_pairs[0]

        matched = best_item if best_score >= self.threshold else None
        return MatchResult(
            query=query,
            matched=matched,
            score=best_score,
            top_k=top_k_pairs,
        )

    def explain(self, query: str, k: int = 3) -> str:
        """人类可读的匹配说明。"""
        result = self.match(query, k=k)
        lines = [f"用户问: {result.query}", f"最佳相似度: {result.score:.4f}"]
        if result.matched:
            lines.append(f"命中标准问: {result.matched.question}")
            lines.append(f"推荐回答: {result.matched.answer}")
        else:
            lines.append(f"未达阈值 {self.threshold}，建议转人工或扩充 FAQ。")
        lines.append("Top-K:")
        for item, score in result.top_k:
            lines.append(f"  [{score:.4f}] {item.question}")
        return "\n".join(lines)


DEMO_QUERIES = [
    "怎么退款啊？",
    "退款什么时候能到账",
    "我想改密码",
    "发货要多久",
    "工单系统怎么对接 API",
]


def main() -> None:
    print("=" * 60)
    print("Day 20 · 相似问匹配工具")
    print("=" * 60)

    matcher = SimilarQuestionMatcher()
    matcher.load()

    queries = DEMO_QUERIES
    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]

    for q in queries:
        print("\n" + "-" * 50)
        print(matcher.explain(q))

    print("\n✅ similar_question_matcher.py 完成")


if __name__ == "__main__":
    main()
