# -*- coding: utf-8 -*-
"""Hybrid Retriever：BM25 + 向量检索 + RRF 融合。"""

from __future__ import annotations

from dataclasses import dataclass, field

from rank_bm25 import BM25Okapi

from .rag_common import cosine_similarity, mock_embed_text, reciprocal_rank_fusion, tokenize_zh


@dataclass
class ChunkHit:
    chunk_id: str
    content: str
    source: str
    bm25_rank: int | None = None
    vector_rank: int | None = None
    rrf_score: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class IndexedChunk:
    chunk_id: str
    content: str
    source: str
    embedding: list[float]
    chunk_index: int = 0


class HybridRetriever:
    """BM25 + 向量双路检索，RRF 融合。"""

    def __init__(self, chunks: list[IndexedChunk]) -> None:
        self.chunks = chunks
        self._id_to_chunk = {c.chunk_id: c for c in chunks}
        self._corpus_tokens = [tokenize_zh(c.content) for c in chunks]
        self._bm25 = BM25Okapi(self._corpus_tokens) if chunks else None

    def bm25_search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if not self.chunks or self._bm25 is None:
            return []
        tokens = tokenize_zh(query)
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(
            zip([c.chunk_id for c in self.chunks], scores),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:top_k]

    def vector_search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if not self.chunks:
            return []
        q_vec = mock_embed_text(query, model="mock-hybrid-kb")
        scored: list[tuple[str, float]] = []
        for chunk in self.chunks:
            score = cosine_similarity(q_vec, chunk.embedding)
            scored.append((chunk.chunk_id, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def retrieve(self, query: str, top_k: int = 5, rrf_k: int = 60) -> list[ChunkHit]:
        if not self.chunks:
            return []

        bm25_ranked = self.bm25_search(query, top_k=top_k * 2)
        vec_ranked = self.vector_search(query, top_k=top_k * 2)

        bm25_ids = [d for d, _ in bm25_ranked]
        vec_ids = [d for d, _ in vec_ranked]
        fused = reciprocal_rank_fusion([bm25_ids, vec_ids], k=rrf_k, top_n=top_k)

        bm25_pos = {d: i + 1 for i, (d, _) in enumerate(bm25_ranked)}
        vec_pos = {d: i + 1 for i, (d, _) in enumerate(vec_ranked)}

        hits: list[ChunkHit] = []
        for chunk_id, score in fused:
            chunk = self._id_to_chunk[chunk_id]
            hits.append(
                ChunkHit(
                    chunk_id=chunk_id,
                    content=chunk.content,
                    source=chunk.source,
                    bm25_rank=bm25_pos.get(chunk_id),
                    vector_rank=vec_pos.get(chunk_id),
                    rrf_score=round(score, 6),
                    metadata={"chunk_index": chunk.chunk_index},
                )
            )
        return hits
