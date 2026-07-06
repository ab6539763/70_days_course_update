# -*- coding: utf-8 -*-
"""Day 67 · 白板编程小练习。"""

from __future__ import annotations


def top_k_similar(query_vec: list[float], doc_vecs: list[list[float]], k: int = 3) -> list[int]:
    """余弦相似度 Top-K（简化）。"""
    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))
    def norm(a):
        return sum(x * x for x in a) ** 0.5
    scores = []
    qn = norm(query_vec) or 1.0
    for i, d in enumerate(doc_vecs):
        dn = norm(d) or 1.0
        scores.append((dot(query_vec, d) / (qn * dn), i))
    scores.sort(reverse=True)
    return [i for _, i in scores[:k]]


if __name__ == "__main__":
    q = [1.0, 0.0]
    docs = [[0.9, 0.1], [0.1, 0.9], [1.0, 0.0]]
    print(top_k_similar(q, docs, k=2))
