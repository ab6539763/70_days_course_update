# -*- coding: utf-8 -*-
"""
Day 29 · Mock / Live Embeddings

无 OPENAI_API_KEY 时使用确定性 mock 向量（与 Day 20 思路一致）。
实现 LangChain Embeddings 接口，供 Chroma 使用。
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
DEFAULT_MODEL = "text-embedding-3-small"

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
    """确定性 mock embedding。"""
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

    for _topic, keywords in TOPIC_KEYWORDS.items():
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
    """LangChain 兼容 mock Embeddings。"""

    def __init__(self, dim: int = MOCK_DIM) -> None:
        self.dim = dim

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [mock_embed_text(t, self.dim) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return mock_embed_text(text, self.dim)


class SparkOpenAIEmbeddings(Embeddings):
    """OpenAI 兼容 live Embeddings。"""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _call_api(self, texts: list[str]) -> list[list[float]]:
        if requests is None:  # pragma: no cover
            raise RuntimeError("需要安装 requests")
        url = f"{self.base_url}/embeddings"
        payload: dict[str, Any] = {"model": self.model, "input": texts}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()["data"]
        data.sort(key=lambda x: x["index"])
        return [item["embedding"] for item in data]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        # 批量请求，避免过长单次 payload
        batch_size = 32
        vectors: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            vectors.extend(self._call_api(texts[i : i + batch_size]))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self._call_api([text])[0]


def get_embeddings(force_mock: bool | None = None) -> Embeddings:
    """根据环境变量返回 mock 或 live Embeddings。"""
    load_dotenv_file()
    if force_mock is None:
        force_mock = os.getenv("SPARKTECH_MOCK", "").strip() in ("1", "true", "yes")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if force_mock or not api_key:
        return SparkMockEmbeddings()
    return SparkOpenAIEmbeddings(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL),
        model=os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_MODEL),
    )


def is_mock_mode() -> bool:
    load_dotenv_file()
    if os.getenv("SPARKTECH_MOCK", "").strip() in ("1", "true", "yes"):
        return True
    return not bool(os.getenv("OPENAI_API_KEY", "").strip())


if __name__ == "__main__":
    emb = get_embeddings(force_mock=True)
    v1 = emb.embed_query("如何申请退款")
    v2 = emb.embed_query("退款流程是什么")
    v3 = emb.embed_query("今天天气怎么样")
    sim12 = np.dot(v1, v2)
    sim13 = np.dot(v1, v3)
    print(f"mock dim={len(v1)}")
    print(f"退款 vs 退款流程 dot={sim12:.4f}")
    print(f"退款 vs 天气 dot={sim13:.4f}")
