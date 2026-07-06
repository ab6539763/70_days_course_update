# -*- coding: utf-8 -*-
"""Day 31-33 共享 RAG 工具：mock embedding、文档加载、评估指标。"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

import numpy as np

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

MOCK_DIM = 64
DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_CORPUS = DATA_DIR / "sparktech_kb.txt"


def load_dotenv_file() -> None:
    if load_dotenv is None:
        return
    code_dir = Path(__file__).resolve().parent
    for candidate in (code_dir / ".env", code_dir.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()


def is_mock_mode() -> bool:
    load_dotenv_file()
    flag = os.getenv("SPARKTECH_MOCK", "1").strip().lower()
    if flag in {"0", "false", "no", "off"}:
        return not bool(os.getenv("OPENAI_API_KEY", "").strip())
    return True


def mock_embed_text(text: str, dim: int = MOCK_DIM, model: str = "mock") -> list[float]:
    """确定性 mock embedding，支持 model 后缀区分「不同模型」。"""
    text = text.strip().lower()
    vec = np.zeros(dim, dtype=np.float64)
    seed = f"{model}::{text}"
    for i in range(len(text)):
        for j in range(i + 1, min(i + 4, len(text) + 1)):
            gram = text[i:j]
            digest = hashlib.md5(f"{seed}::{gram}".encode("utf-8")).hexdigest()
            h = int(digest, 16)
            idx = h % dim
            sign = 1.0 if (h >> 4) % 2 == 0 else -1.0
            vec[idx] += sign
    norm = np.linalg.norm(vec)
    if norm > 1e-9:
        vec = vec / norm
    return vec.tolist()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a, dtype=np.float64), np.array(b, dtype=np.float64)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom < 1e-12:
        return 0.0
    return float(np.dot(va, vb) / denom)


def load_corpus(path: Path | None = None) -> str:
    p = path or DEFAULT_CORPUS
    return p.read_text(encoding="utf-8")


def split_by_headings(text: str) -> list[dict[str, str]]:
    """按 ## 标题切分为父文档块。"""
    sections: list[dict[str, str]] = []
    current_title = "前言"
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append(
                    {"title": current_title, "content": "\n".join(current_lines).strip()}
                )
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections.append({"title": current_title, "content": "\n".join(current_lines).strip()})
    return [s for s in sections if s["content"]]


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    """固定字符窗口切块（教学用，与 LangChain splitter 参数对齐）。"""
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def tokenize_zh(text: str) -> list[str]:
    """简易中文分词：字符 + 英文词。"""
    text = text.lower()
    tokens: list[str] = []
    for word in re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", text):
        tokens.append(word)
    return tokens or list(text)


class MockEmbeddingModel:
    """LangChain 兼容的 mock Embeddings 封装。"""

    def __init__(self, model_name: str = "mock-hash", dim: int = MOCK_DIM) -> None:
        self.model_name = model_name
        self.dim = dim

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [mock_embed_text(t, self.dim, self.model_name) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return mock_embed_text(text, self.dim, self.model_name)


def get_langchain_embeddings(model_name: str = "text-embedding-3-small"):
    """返回 LangChain Embeddings；无 Key 时回退 mock。"""
    load_dotenv_file()
    if is_mock_mode():
        return MockEmbeddingModel(model_name=f"mock-{model_name}")

    try:
        from langchain_openai import OpenAIEmbeddings
    except ImportError:
        return MockEmbeddingModel(model_name=f"mock-{model_name}")

    return OpenAIEmbeddings(
        model=model_name,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )


def reciprocal_rank_fusion(
    ranked_lists: list[list[str]], k: int = 60, top_n: int = 5
) -> list[tuple[str, float]]:
    """RRF 融合多个排序列表。返回 (doc_id, score)。"""
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ordered[:top_n]


def hit_at_k(retrieved: list[str], expected_keywords: list[str], k: int = 3) -> bool:
    """教学指标：top-k 是否包含任一期望关键词。"""
    top = retrieved[:k]
    blob = " ".join(top).lower()
    return any(kw.lower() in blob for kw in expected_keywords)
