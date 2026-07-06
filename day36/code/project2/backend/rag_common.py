# -*- coding: utf-8 -*-
"""RAG 共享工具：mock embedding、分词、RRF 融合。"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

import numpy as np

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

MOCK_DIM = 64
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_dotenv_file() -> None:
    if load_dotenv is None:
        return
    for candidate in (PROJECT_ROOT / ".env", PROJECT_ROOT.parent / ".env"):
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


def mock_embed_text(text: str, dim: int = MOCK_DIM, model: str = "mock-kb") -> list[float]:
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


def embedding_to_json(vec: list[float]) -> str:
    return json.dumps(vec, ensure_ascii=False)


def embedding_from_json(raw: str | None) -> list[float]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return [float(x) for x in data]
    except (json.JSONDecodeError, TypeError, ValueError):
        return []


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a, dtype=np.float64), np.array(b, dtype=np.float64)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom < 1e-12:
        return 0.0
    return float(np.dot(va, vb) / denom)


def tokenize_zh(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", text)
    return tokens or list(text)


def reciprocal_rank_fusion(
    ranked_lists: list[list[str]], k: int = 60, top_n: int = 5
) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ordered[:top_n]


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
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


def make_snippet(text: str, max_len: int = 120) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3] + "..."
