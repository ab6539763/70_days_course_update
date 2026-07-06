# -*- coding: utf-8 -*-
"""RAG 服务：Hybrid 检索 + Rerank + 引用生成 + Mock/Live 回答。"""

from __future__ import annotations

import json
import os
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass

from sqlalchemy.orm import Session

from .hybrid_retriever import HybridRetriever, IndexedChunk
from .models import KnowledgeChunk
from .rag_common import embedding_from_json, is_mock_mode, make_snippet
from .rerank import rerank
from .schemas import CitationOut


class RAGServiceError(Exception):
    pass


@dataclass
class RAGAnswer:
    text: str
    citations: list[CitationOut]
    mode: str


class RAGService:
    """企业知识库问答核心服务。"""

    def __init__(self) -> None:
        self._retriever: HybridRetriever | None = None
        self._chunk_count = 0

    @property
    def mode(self) -> str:
        return "mock" if is_mock_mode() else "live"

    @property
    def chunk_count(self) -> int:
        return self._chunk_count

    def load_index(self, db: Session) -> None:
        rows = db.query(KnowledgeChunk).order_by(KnowledgeChunk.id.asc()).all()
        indexed: list[IndexedChunk] = []
        for row in rows:
            indexed.append(
                IndexedChunk(
                    chunk_id=row.chunk_id,
                    content=row.content,
                    source=row.source,
                    embedding=embedding_from_json(row.embedding_json),
                    chunk_index=row.chunk_index,
                )
            )
        self._retriever = HybridRetriever(indexed)
        self._chunk_count = len(indexed)

    def _ensure_index(self, db: Session) -> None:
        if self._retriever is None or self._chunk_count == 0:
            self.load_index(db)

    def retrieve(self, db: Session, query: str, top_k: int = 3) -> list[CitationOut]:
        self._ensure_index(db)
        if not self._retriever or not self._retriever.chunks:
            return []

        hits = self._retriever.retrieve(query, top_k=top_k * 2)
        reranked = rerank(query, hits, top_k=top_k)

        citations: list[CitationOut] = []
        for hit in reranked:
            citations.append(
                CitationOut(
                    chunk_id=hit.chunk_id,
                    source=hit.source,
                    snippet=make_snippet(hit.content),
                    score=hit.rrf_score,
                    chunk_index=int(hit.metadata.get("chunk_index", 0)),
                )
            )
        return citations

    def _build_context(self, citations: list[CitationOut]) -> str:
        if not citations:
            return ""
        parts: list[str] = []
        for i, cite in enumerate(citations, start=1):
            parts.append(f"[{i}] 来源:{cite.source}\n{cite.snippet}")
        return "\n\n".join(parts)

    def _mock_generate(self, query: str, citations: list[CitationOut]) -> str:
        if not citations:
            return (
                "抱歉，我在当前知识库中没有找到与您问题相关的内容。"
                "请尝试上传相关文档，或换一种问法。"
            )

        top = citations[0]
        keywords = re.findall(r"[\u4e00-\u9fff]{2,}", query)
        keyword_hint = "、".join(keywords[:3]) if keywords else query[:20]

        body_parts: list[str] = []
        for i, cite in enumerate(citations[:3], start=1):
            body_parts.append(f"根据《{cite.source}》[{i}]：{cite.snippet}")

        answer = (
            f"关于「{keyword_hint}」，知识库检索到 {len(citations)} 条相关片段。\n"
            + "\n".join(body_parts)
            + f"\n\n（mock 模式 · 最高分来源 [{top.source}] score={top.score:.3f}）"
        )
        return answer

    def _live_generate(self, query: str, context: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RAGServiceError("live 模式需要 openai 包") from exc

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RAGServiceError("未配置 OPENAI_API_KEY")

        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )
        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        system = (
            "你是星火智服企业知识库助手。仅根据提供的参考资料回答；"
            "若资料不足请明确说明不知道。回答末尾用 [1][2] 标注引用编号。"
        )
        user = f"参考资料：\n{context}\n\n用户问题：{query}"
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()

    def ask(self, db: Session, query: str, top_k: int = 3) -> RAGAnswer:
        citations = self.retrieve(db, query, top_k=top_k)
        context = self._build_context(citations)

        if is_mock_mode():
            text = self._mock_generate(query, citations)
        else:
            if not context:
                text = self._mock_generate(query, [])
            else:
                text = self._live_generate(query, context)

        return RAGAnswer(text=text, citations=citations, mode=self.mode)

    def stream_answer(
        self, db: Session, query: str, top_k: int = 3, chunk_size: int = 8
    ) -> Iterator[tuple[str, list[CitationOut] | None, str | None]]:
        """
        流式生成。

        Yields:
            (event_type, citations_or_none, delta_or_none)
            event_type: citations | delta | done
        """
        citations = self.retrieve(db, query, top_k=top_k)
        yield ("citations", citations, None)

        if is_mock_mode():
            full = self._mock_generate(query, citations)
            for i in range(0, len(full), chunk_size):
                yield ("delta", None, full[i : i + chunk_size])
                time.sleep(0.02)
            yield ("done", citations, None)
            return

        context = self._build_context(citations)
        if not context:
            full = self._mock_generate(query, [])
            for i in range(0, len(full), chunk_size):
                yield ("delta", None, full[i : i + chunk_size])
                time.sleep(0.02)
            yield ("done", [], None)
            return

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RAGServiceError("live 模式需要 openai 包") from exc

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RAGServiceError("未配置 OPENAI_API_KEY")

        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )
        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        system = (
            "你是星火智服企业知识库助手。仅根据参考资料回答，并标注 [1][2] 引用。"
        )
        user = f"参考资料：\n{context}\n\n用户问题：{query}"

        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield ("delta", None, delta)
        yield ("done", citations, None)


def citations_to_json(citations: list[CitationOut]) -> str:
    return json.dumps([c.model_dump() for c in citations], ensure_ascii=False)


def citations_from_json(raw: str | None) -> list[CitationOut]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return [CitationOut.model_validate(item) for item in data]
    except (json.JSONDecodeError, TypeError, ValueError):
        return []


_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
