# -*- coding: utf-8 -*-
"""Lightweight document RAG over sample_docs (keyword overlap, mock embeddings)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from backend.config import SAMPLE_DOCS_DIR

_INDEX: list[dict[str, Any]] = []


def _tokenize(text: str) -> set[str]:
    parts = re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}", text.lower())
    return set(parts)


def _score(query_tokens: set[str], doc_tokens: set[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    overlap = len(query_tokens & doc_tokens)
    return overlap / max(len(query_tokens), 1)


def build_rag_index() -> int:
    """扫描 sample_docs 构建内存索引。"""
    global _INDEX
    _INDEX = []
    if not SAMPLE_DOCS_DIR.exists():
        SAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(SAMPLE_DOCS_DIR.glob("*")):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for i, chunk in enumerate(_chunk_text(text)):
            _INDEX.append(
                {
                    "source": path.name,
                    "chunk_id": f"{path.stem}-{i}",
                    "snippet": chunk.strip(),
                    "tokens": _tokenize(chunk),
                }
            )
    return len(_INDEX)


def _chunk_text(text: str, size: int = 280, overlap: int = 40) -> list[str]:
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += max(size - overlap, 1)
    return chunks


def document_rag_search(query: str, top_k: int = 3) -> dict[str, Any]:
    """检索公司内部文档片段。"""
    if not _INDEX:
        build_rag_index()
    q_tokens = _tokenize(query)
    ranked = sorted(
        (
            {
                "source": row["source"],
                "chunk_id": row["chunk_id"],
                "snippet": row["snippet"],
                "score": round(_score(q_tokens, row["tokens"]), 4),
            }
            for row in _INDEX
        ),
        key=lambda x: x["score"],
        reverse=True,
    )
    hits = [h for h in ranked if h["score"] > 0][:top_k]
    if not hits and ranked:
        hits = ranked[:1]
    return {"tool": "document_rag_search", "query": query, "hits": hits}


def reset_rag_index() -> None:
    global _INDEX
    _INDEX = []
