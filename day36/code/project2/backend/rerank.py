# -*- coding: utf-8 -*-
"""Rerank：mock 交叉编码器重排（可替换为 bge-reranker）。"""

from __future__ import annotations

import re

from .hybrid_retriever import ChunkHit
from .rag_common import tokenize_zh


def _keyword_overlap_score(query: str, content: str) -> float:
    """教学用 mock rerank：查询词与文档重叠度。"""
    q_tokens = set(tokenize_zh(query))
    c_tokens = set(tokenize_zh(content))
    if not q_tokens:
        return 0.0
    overlap = len(q_tokens & c_tokens)
    return overlap / len(q_tokens)


def _exact_phrase_bonus(query: str, content: str) -> float:
    q = query.strip().lower()
    c = content.lower()
    bonus = 0.0
    for phrase in re.findall(r"[\u4e00-\u9fff]{2,}|[a-z0-9]{3,}", q):
        if phrase in c:
            bonus += 0.15
    return min(bonus, 0.45)


def rerank(query: str, hits: list[ChunkHit], top_k: int = 3) -> list[ChunkHit]:
    """对 Hybrid 结果重排，综合 RRF 分与关键词重叠。"""
    if not hits:
        return []

    scored: list[tuple[float, ChunkHit]] = []
    for hit in hits:
        overlap = _keyword_overlap_score(query, hit.content)
        phrase = _exact_phrase_bonus(query, hit.content)
        final = hit.rrf_score * 0.55 + overlap * 0.35 + phrase * 0.10
        scored.append((final, hit))

    scored.sort(key=lambda x: x[0], reverse=True)
    result: list[ChunkHit] = []
    for score, hit in scored[:top_k]:
        hit.rrf_score = round(score, 6)
        result.append(hit)
    return result
