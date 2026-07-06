# -*- coding: utf-8 -*-
"""
Day 20 · 余弦相似度（纯 NumPy 实现）

不依赖 API，用于向量检索与相似问匹配的基础运算。
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def cosine_similarity(a: NDArray[np.floating], b: NDArray[np.floating]) -> float:
    """
    计算两个向量的余弦相似度，范围 [-1, 1]。

    cos(θ) = (a · b) / (||a|| * ||b||)
    """
    a = np.asarray(a, dtype=np.float64).flatten()
    b = np.asarray(b, dtype=np.float64).flatten()
    if a.shape != b.shape:
        raise ValueError(f"向量维度不一致: {a.shape} vs {b.shape}")

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def cosine_similarity_matrix(
    vectors: NDArray[np.floating],
) -> NDArray[np.floating]:
    """计算向量矩阵的 pairwise 余弦相似度（对称矩阵）。"""
    vectors = np.asarray(vectors, dtype=np.float64)
    if vectors.ndim != 2:
        raise ValueError("vectors 应为二维矩阵 (n_samples, dim)")

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-12, norms)
    normalized = vectors / norms
    return normalized @ normalized.T


def top_k_similar(
    query: NDArray[np.floating],
    corpus: NDArray[np.floating],
    k: int = 3,
) -> list[tuple[int, float]]:
    """返回 corpus 中与 query 最相似的 top-k 索引及分数。"""
    query = np.asarray(query, dtype=np.float64).flatten()
    corpus = np.asarray(corpus, dtype=np.float64)
    if corpus.ndim != 2:
        raise ValueError("corpus 应为二维矩阵")

    scores = np.array([cosine_similarity(query, row) for row in corpus])
    k = min(k, len(scores))
    top_indices = np.argsort(scores)[::-1][:k]
    return [(int(i), float(scores[i])) for i in top_indices]


def main() -> None:
    print("=" * 60)
    print("Day 20 · cosine_similarity.py")
    print("=" * 60)

    # 二维直观示例
    v1 = np.array([1.0, 0.0])
    v2 = np.array([1.0, 1.0])
    v3 = np.array([-1.0, 0.0])

    print(f"\ncos([1,0], [1,1]) = {cosine_similarity(v1, v2):.4f}")
    print(f"cos([1,0], [-1,0]) = {cosine_similarity(v1, v3):.4f}")

    # 高维 mock 向量
    rng = np.random.default_rng(42)
    corpus = rng.normal(size=(5, 16))
    query = corpus[2] + rng.normal(scale=0.05, size=16)

    print("\nTop-3 相似索引:")
    for idx, score in top_k_similar(query, corpus, k=3):
        print(f"  idx={idx}  score={score:.4f}")

    print("\n相似度矩阵对角线（应全为 1.0）:")
    mat = cosine_similarity_matrix(corpus)
    print(np.round(np.diag(mat), 4))

    print("\n✅ cosine_similarity.py 完成")


if __name__ == "__main__":
    main()
