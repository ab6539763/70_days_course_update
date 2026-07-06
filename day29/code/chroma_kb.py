# -*- coding: utf-8 -*-
"""
Day 29 · Chroma 知识库封装

提供集合创建、文档写入、相似检索、Retriever 导出。

运行：cd day29/code && python3 chroma_kb.py
"""

from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever

from mock_embeddings import get_embeddings, is_mock_mode

CODE_DIR = Path(__file__).resolve().parent
DEFAULT_PERSIST_DIR = Path(
    os.getenv("CHROMA_PERSIST_DIR", str(Path(tempfile.gettempdir()) / "sparktech_day29_chroma"))
)
DEFAULT_COLLECTION = "sparktech_kb"


@dataclass
class SearchHit:
    content: str
    metadata: dict[str, Any]
    score: float

    def source_label(self) -> str:
        src = self.metadata.get("source", "unknown")
        return Path(str(src)).name


class ChromaKnowledgeBase:
    """星火智服 Chroma 知识库薄封装。"""

    def __init__(
        self,
        persist_directory: Path | str | None = None,
        collection_name: str = DEFAULT_COLLECTION,
        embedding: Embeddings | None = None,
    ) -> None:
        env_persist = os.getenv("CHROMA_PERSIST_DIR", "").strip()
        if persist_directory is not None:
            self.persist_directory = Path(persist_directory)
        elif env_persist and env_persist not in ("memory", ":memory:"):
            self.persist_directory = Path(env_persist)
        else:
            self.persist_directory = Path(tempfile.mkdtemp(prefix="sparktech_day29_chroma_"))
        self.collection_name = collection_name
        self.embedding = embedding or get_embeddings()
        self._store: Chroma | None = None

    @property
    def mode(self) -> str:
        return "mock" if is_mock_mode() else "live"

    def _get_store(self) -> Chroma:
        if self._store is None:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self._store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding,
                persist_directory=str(self.persist_directory),
            )
        return self._store

    def add_documents(self, docs: list[Document]) -> list[str]:
        if not docs:
            return []
        return self._get_store().add_documents(docs)

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        return self._get_store().similarity_search(query, k=k)

    def similarity_search_with_score(self, query: str, k: int = 4) -> list[SearchHit]:
        results = self._get_store().similarity_search_with_score(query, k=k)
        hits: list[SearchHit] = []
        for doc, score in results:
            # Chroma 默认距离越小越相似；转为 similarity 分数（越大越好）
            similarity = 1.0 / (1.0 + float(score))
            hits.append(SearchHit(content=doc.page_content, metadata=doc.metadata, score=similarity))
        return hits

    def as_retriever(self, search_kwargs: dict[str, Any] | None = None) -> VectorStoreRetriever:
        kwargs = search_kwargs or {"k": 4}
        return self._get_store().as_retriever(search_kwargs=kwargs)

    def count(self) -> int:
        store = self._get_store()
        try:
            data = store._collection.get()  # noqa: SLF001 — 教学用
            return len(data.get("ids", []))
        except Exception:
            return 0

    def reset(self) -> None:
        """清空持久化目录（教学重置）。"""
        self._store = None
        if self.persist_directory.exists():
            shutil.rmtree(self.persist_directory, ignore_errors=True)
        self.persist_directory = Path(tempfile.mkdtemp(prefix="sparktech_day29_chroma_"))
        self.persist_directory.mkdir(parents=True, exist_ok=True)


def demo() -> None:
    kb = ChromaKnowledgeBase()
    kb.reset()

    docs = [
        Document(page_content="客户可在工单系统申请退款，三个工作日内审核。", metadata={"source": "faq_refund.txt"}),
        Document(page_content="大模型回答仅供参考，退款须经人工客服确认。", metadata={"source": "service_policy.txt"}),
        Document(page_content="星火智服支持 RAG 检索增强生成。", metadata={"source": "llm_intro.md"}),
    ]
    ids = kb.add_documents(docs)
    print(f"mode={kb.mode} added={len(ids)} total={kb.count()}")

    query = "怎么退款"
    hits = kb.similarity_search_with_score(query, k=2)
    print(f"\nquery: {query}")
    for i, hit in enumerate(hits):
        print(f"  #{i} score={hit.score:.4f} source={hit.source_label()}")
        print(f"      {hit.content[:60]}...")

    retriever = kb.as_retriever(search_kwargs={"k": 2})
    retrieved = retriever.invoke(query)
    print(f"\nretriever returned {len(retrieved)} docs")


if __name__ == "__main__":
    demo()
