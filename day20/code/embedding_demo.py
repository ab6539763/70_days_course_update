# -*- coding: utf-8 -*-
"""
Day 20 · Embedding 模型演示

- live 模式：调用 OpenAI 兼容 embeddings API
- mock 模式：确定性哈希向量（无 Key 可跑，维度固定 64）
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
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


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "text-embedding-3-small"
MOCK_DIM = 64
ENV_API_KEY = "OPENAI_API_KEY"
ENV_BASE_URL = "OPENAI_BASE_URL"
ENV_EMBED_MODEL = "OPENAI_EMBEDDING_MODEL"


@dataclass
class EmbeddingResult:
    text: str
    vector: list[float]
    model: str
    mode: str
    latency_ms: float = 0.0
    dimensions: int = 0
    raw: dict[str, Any] = field(default_factory=dict)


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
    """
    确定性 mock embedding：字符 n-gram + 主题关键词特征。

    同一文本永远得到同一向量；语义相近的中文问句相似度更高（教学用）。
    """
    text = text.strip().lower()
    vec = np.zeros(dim, dtype=np.float64)

    # 字符 n-gram 特征哈希
    for i in range(len(text)):
        for j in range(i + 1, min(i + 4, len(text) + 1)):
            gram = text[i:j]
            digest = hashlib.md5(gram.encode("utf-8")).hexdigest()
            h = int(digest, 16)
            idx = h % dim
            sign = 1.0 if (h >> 4) % 2 == 0 else -1.0
            vec[idx] += sign

    # 主题关键词增强（FAQ 常见意图）
    topic_keywords: dict[str, list[int]] = {
        "退款": [0, 1, 2, 3],
        "到账": [0, 1, 4],
        "密码": [5, 6, 7],
        "登录": [5, 8],
        "物流": [9, 10, 11],
        "发货": [9, 10, 12],
        "运单": [9, 13],
        "发票": [14, 15, 16],
        "工单": [17, 18, 19],
        "api": [17, 20, 21],
        "集成": [17, 22],
        "embedding": [23, 24, 25],
        "向量": [23, 26],
        "相似": [23, 27],
    }
    for kw, indices in topic_keywords.items():
        if kw in text:
            for idx in indices:
                vec[idx % dim] += 2.5

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


class EmbeddingClient:
    """轻量 Embedding 客户端。"""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        mock_dim: int = MOCK_DIM,
        timeout: float = 30.0,
    ) -> None:
        load_dotenv_file()
        self._api_key = (api_key or os.getenv(ENV_API_KEY) or "").strip()
        self._base_url = (base_url or os.getenv(ENV_BASE_URL) or DEFAULT_BASE_URL).rstrip("/")
        self._model = model or os.getenv(ENV_EMBED_MODEL) or DEFAULT_MODEL
        self._mock_dim = mock_dim
        self._timeout = timeout

    @property
    def is_mock_mode(self) -> bool:
        return not self._api_key

    @property
    def mode(self) -> str:
        return "mock" if self.is_mock_mode else "live"

    def embed(self, text: str) -> EmbeddingResult:
        text = text.strip()
        if not text:
            raise ValueError("text 不能为空")
        if self.is_mock_mode:
            return self._mock_embed(text)
        return self._live_embed(text)

    def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        return [self.embed(t) for t in texts]

    def _mock_embed(self, text: str) -> EmbeddingResult:
        start = time.perf_counter()
        vector = mock_embed_text(text, self._mock_dim)
        latency_ms = (time.perf_counter() - start) * 1000
        return EmbeddingResult(
            text=text,
            vector=vector,
            model=f"mock-hash-{self._mock_dim}",
            mode="mock",
            latency_ms=round(latency_ms, 3),
            dimensions=len(vector),
            raw={"mock": True},
        )

    def _live_embed(self, text: str) -> EmbeddingResult:
        if requests is None:
            raise RuntimeError("未安装 requests")

        url = f"{self._base_url}/embeddings"
        payload = {"model": self._model, "input": text}
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        start = time.perf_counter()
        resp = requests.post(url, headers=headers, json=payload, timeout=self._timeout)
        latency_ms = (time.perf_counter() - start) * 1000

        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        vector = data["data"][0]["embedding"]
        return EmbeddingResult(
            text=text,
            vector=vector,
            model=data.get("model", self._model),
            mode="live",
            latency_ms=round(latency_ms, 2),
            dimensions=len(vector),
            raw=data,
        )


def main() -> None:
    print("=" * 60)
    print("Day 20 · embedding_demo.py")
    print("=" * 60)

    client = EmbeddingClient()
    print(f"模式: {client.mode}")

    samples = [
        "如何申请退款？",
        "退款流程是什么？",
        "忘记密码怎么办？",
    ]

    results = client.embed_batch(samples)
    for r in results:
        print(f"\n文本: {r.text}")
        print(f"  dim={r.dimensions}  前5维={r.vector[:5]}")

    # 相似度预览
    from cosine_similarity import cosine_similarity

    sim_01 = cosine_similarity(np.array(results[0].vector), np.array(results[1].vector))
    sim_02 = cosine_similarity(np.array(results[0].vector), np.array(results[2].vector))
    print(f"\n「退款」vs「退款流程」相似度: {sim_01:.4f}")
    print(f"「退款」vs「忘记密码」相似度: {sim_02:.4f}")

    print("\n✅ embedding_demo.py 完成")


if __name__ == "__main__":
    main()
