# -*- coding: utf-8 -*-
"""
Day 30 · Mock / Live Embeddings（与 Day 29 一致）
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

import numpy as np

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]

from langchain_core.embeddings import Embeddings

MOCK_DIM = 64
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_EMBED_MODEL = "text-embedding-3-small"
DEFAULT_CHAT_MODEL = "gpt-4o-mini"

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "refund": ["退款", "退钱", "返还", "退费"],
    "ticket": ["工单", "ticket", "case"],
    "llm": ["大模型", "llm", "gpt", "embedding", "rag"],
    "order": ["订单", "order", "st-"],
    "service": ["客服", "服务", "响应"],
}


def load_dotenv_file() -> None:
    if load_dotenv is None:
        return
    code_dir = Path(__file__).resolve().parent
    for candidate in (code_dir / ".env", code_dir.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()


def mock_embed_text(text: str, dim: int = MOCK_DIM) -> list[float]:
    text_norm = text.strip().lower()
    vec = np.zeros(dim, dtype=np.float64)
    for i in range(len(text_norm)):
        for j in range(i + 1, min(i + 4, len(text_norm) + 1)):
            gram = text_norm[i:j]
            digest = hashlib.md5(gram.encode("utf-8")).hexdigest()
            h = int(digest, 16)
            idx = h % dim
            sign = 1.0 if (h >> 4) % 2 == 0 else -1.0
            vec[idx] += sign
    for keywords in TOPIC_KEYWORDS.values():
        for kw in keywords:
            if kw.lower() in text_norm:
                digest = hashlib.sha256(kw.encode("utf-8")).hexdigest()
                h = int(digest, 16)
                vec[h % dim] += 2.5
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


class SparkMockEmbeddings(Embeddings):
    def __init__(self, dim: int = MOCK_DIM) -> None:
        self.dim = dim

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [mock_embed_text(t, self.dim) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return mock_embed_text(text, self.dim)


class SparkOpenAIEmbeddings(Embeddings):
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, model: str = DEFAULT_EMBED_MODEL) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _call_api(self, texts: list[str]) -> list[list[float]]:
        if requests is None:  # pragma: no cover
            raise RuntimeError("需要 requests")
        resp = requests.post(
            f"{self.base_url}/embeddings",
            json={"model": self.model, "input": texts},
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        data.sort(key=lambda x: x["index"])
        return [item["embedding"] for item in data]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for i in range(0, len(texts), 32):
            vectors.extend(self._call_api(texts[i : i + 32]))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self._call_api([text])[0]


def get_embeddings(force_mock: bool | None = None) -> Embeddings:
    load_dotenv_file()
    if force_mock is None:
        force_mock = os.getenv("SPARKTECH_MOCK", "").strip() in ("1", "true", "yes")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if force_mock or not api_key:
        return SparkMockEmbeddings()
    return SparkOpenAIEmbeddings(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL),
        model=os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBED_MODEL),
    )


def is_mock_mode() -> bool:
    load_dotenv_file()
    if os.getenv("SPARKTECH_MOCK", "").strip() in ("1", "true", "yes"):
        return True
    return not bool(os.getenv("OPENAI_API_KEY", "").strip())
