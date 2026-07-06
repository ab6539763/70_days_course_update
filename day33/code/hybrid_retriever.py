# -*- coding: utf-8 -*-
"""
Day 33 · Hybrid Retriever：BM25 + 向量检索 + RRF 融合
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi

from rag_common import cosine_similarity, load_corpus, mock_embed_text, reciprocal_rank_fusion, tokenize_zh


@dataclass
class HybridHit:
    doc_id: str
    content: str
    bm25_rank: int | None = None
    vector_rank: int | None = None
    rrf_score: float = 0.0
    metadata: dict = field(default_factory=dict)


class HybridRetriever:
    """BM25 + 向量双路检索，RRF 融合。"""

    def __init__(self, docs: list[Document], doc_ids: list[str] | None = None) -> None:
        self.docs = docs
        self.doc_ids = doc_ids or [f"doc-{i}" for i in range(len(docs))]
        self._corpus_tokens = [tokenize_zh(d.page_content) for d in docs]
        self._bm25 = BM25Okapi(self._corpus_tokens)

    def bm25_search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        tokens = tokenize_zh(query)
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(
            zip(self.doc_ids, scores),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:top_k]

    def vector_search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        q_vec = mock_embed_text(query, model="mock-hybrid")
        scored: list[tuple[str, float]] = []
        for doc_id, doc in zip(self.doc_ids, self.docs):
            d_vec = mock_embed_text(doc.page_content, model="mock-hybrid")
            scored.append((doc_id, cosine_similarity(q_vec, d_vec)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def retrieve(self, query: str, top_k: int = 5, rrf_k: int = 60) -> list[HybridHit]:
        bm25_ranked = self.bm25_search(query, top_k=top_k * 2)
        vec_ranked = self.vector_search(query, top_k=top_k * 2)

        bm25_ids = [d for d, _ in bm25_ranked]
        vec_ids = [d for d, _ in vec_ranked]
        fused = reciprocal_rank_fusion([bm25_ids, vec_ids], k=rrf_k, top_n=top_k)

        id_to_doc = dict(zip(self.doc_ids, self.docs))
        bm25_pos = {d: i + 1 for i, (d, _) in enumerate(bm25_ranked)}
        vec_pos = {d: i + 1 for i, (d, _) in enumerate(vec_ranked)}

        hits: list[HybridHit] = []
        for doc_id, score in fused:
            doc = id_to_doc[doc_id]
            hits.append(
                HybridHit(
                    doc_id=doc_id,
                    content=doc.page_content,
                    bm25_rank=bm25_pos.get(doc_id),
                    vector_rank=vec_pos.get(doc_id),
                    rrf_score=round(score, 6),
                    metadata=dict(doc.metadata),
                )
            )
        return hits


def build_child_docs(corpus: str, chunk_size: int = 200) -> list[Document]:
    """较小 chunk 用于检索（parent 检索铺垫）。"""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=40)
    return splitter.create_documents([corpus])


def main() -> None:
    corpus = load_corpus()
    docs = build_child_docs(corpus)
    retriever = HybridRetriever(docs)
    queries = ["退款 7 天", "API Key 审批", "P0 15 分钟"]
    print("Day 33 · hybrid_retriever (BM25 + Vector + RRF)\n")
    for q in queries:
        hits = retriever.retrieve(q, top_k=3)
        print(f"Q: {q}")
        for h in hits:
            preview = h.content.replace("\n", " ")[:50]
            print(
                f"  {h.doc_id} rrf={h.rrf_score:.4f} "
                f"bm25=#{h.bm25_rank} vec=#{h.vector_rank} | {preview}..."
            )
        print()


if __name__ == "__main__":
    main()
