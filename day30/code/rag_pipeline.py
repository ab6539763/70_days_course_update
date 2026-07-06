# -*- coding: utf-8 -*-
"""
Day 30 · 完整 RAG 流水线

load → split → embed → store → retrieve → generate
支持引用溯源与「我不知道」兜底。

运行：cd day30/code && python3 rag_pipeline.py
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from mock_embeddings import DEFAULT_BASE_URL, DEFAULT_CHAT_MODEL, get_embeddings, is_mock_mode, load_dotenv_file

CODE_DIR = Path(__file__).resolve().parent
WORKSPACE = CODE_DIR.parents[1]
DAY28_DOCS = WORKSPACE / "day28" / "code" / "data" / "sample_docs"
PROMPT_PATH = CODE_DIR / "prompts" / "rag_prompt.txt"
DEFAULT_PERSIST = Path(
    os.getenv("CHROMA_PERSIST_DIR", str(Path(tempfile.gettempdir()) / "sparktech_day30_chroma"))
)
DEFAULT_COLLECTION = "sparktech_rag"
UNKNOWN_REPLY = "我不知道。建议联系人工客服或查阅官方文档。"


@dataclass
class RetrievedChunk:
    content: str
    source: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGAnswer:
    question: str
    answer: str
    citations: list[str]
    chunks: list[RetrievedChunk]
    mode: str
    used_llm: bool
    fallback_unknown: bool


def resolve_docs_dir() -> Path:
    if DAY28_DOCS.is_dir():
        return DAY28_DOCS
    local = CODE_DIR / "data" / "sample_docs"
    if local.is_dir():
        return local
    raise FileNotFoundError("未找到 sample_docs（需要 Day 28 样本）")


def load_documents(docs_dir: Path) -> list[Document]:
    docs: list[Document] = []
    for path in sorted(docs_dir.glob("*.txt")):
        docs.append(Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": str(path)}))
    for path in sorted(docs_dir.glob("*.md")):
        docs.append(Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": str(path)}))
    csv_path = docs_dir / "orders_sample.csv"
    if csv_path.is_file():
        from langchain_community.document_loaders import CSVLoader

        docs.extend(CSVLoader(str(csv_path), encoding="utf-8").load())
    html_path = docs_dir / "sparktech_web.html"
    if html_path.is_file():
        from langchain_community.document_loaders import BSHTMLLoader

        docs.extend(BSHTMLLoader(str(html_path), open_encoding="utf-8").load())
    return docs


def split_documents(docs: list[Document], chunk_size: int = 400, chunk_overlap: int = 60) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )
    return splitter.split_documents(docs)


def source_label(metadata: dict[str, Any]) -> str:
    src = metadata.get("source", "unknown")
    return Path(str(src)).name


class RAGPipeline:
    """星火智服 RAG 全链路。"""

    def __init__(
        self,
        persist_directory: Path | str | None = None,
        collection_name: str = DEFAULT_COLLECTION,
        score_threshold: float | None = None,
    ) -> None:
        load_dotenv_file()
        env_persist = os.getenv("CHROMA_PERSIST_DIR", "").strip()
        if persist_directory is not None:
            self.persist_directory = Path(persist_directory)
        elif env_persist and env_persist not in ("memory", ":memory:"):
            self.persist_directory = Path(env_persist)
        else:
            self.persist_directory = Path(tempfile.mkdtemp(prefix="sparktech_day30_chroma_"))
        self.collection_name = collection_name
        self.embedding = get_embeddings()
        self.score_threshold = score_threshold or float(os.getenv("RAG_SCORE_THRESHOLD", "0.35"))
        self._store: Chroma | None = None
        self._prompt_template = self._load_prompt_template()

    @property
    def mode(self) -> str:
        return "mock" if is_mock_mode() else "live"

    def _load_prompt_template(self) -> str:
        if PROMPT_PATH.is_file():
            return PROMPT_PATH.read_text(encoding="utf-8")
        return (
            "根据上下文回答。\n上下文:\n{context}\n问题:{question}\n"
            "不足则答：我不知道。建议联系人工客服或查阅官方文档。"
        )

    def _get_store(self) -> Chroma:
        if self._store is None:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self._store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding,
                persist_directory=str(self.persist_directory),
            )
        return self._store

    def reset_store(self) -> None:
        self._store = None
        if self.persist_directory.exists():
            shutil.rmtree(self.persist_directory, ignore_errors=True)
        self.persist_directory = Path(tempfile.mkdtemp(prefix="sparktech_day30_chroma_"))
        self.persist_directory.mkdir(parents=True, exist_ok=True)

    def ingest(
        self,
        docs_dir: Path | None = None,
        chunk_size: int = 400,
        chunk_overlap: int = 60,
        reset: bool = True,
    ) -> int:
        """load → split → embed → store"""
        docs_dir = docs_dir or resolve_docs_dir()
        raw = load_documents(docs_dir)
        chunks = split_documents(raw, chunk_size, chunk_overlap)
        if reset:
            self.reset_store()
        if chunks:
            self._get_store().add_documents(chunks)
        return len(chunks)

    def retrieve(self, question: str, k: int = 4) -> list[RetrievedChunk]:
        results = self._get_store().similarity_search_with_score(question, k=k)
        retrieved: list[RetrievedChunk] = []
        for doc, distance in results:
            score = 1.0 / (1.0 + float(distance))
            retrieved.append(
                RetrievedChunk(
                    content=doc.page_content,
                    source=source_label(doc.metadata),
                    score=score,
                    metadata=dict(doc.metadata),
                )
            )
        return retrieved

    def _format_context(self, chunks: list[RetrievedChunk]) -> str:
        parts = []
        for i, ch in enumerate(chunks):
            parts.append(f"[片段{i + 1} | 来源: {ch.source} | 相关度: {ch.score:.3f}]\n{ch.content}")
        return "\n\n".join(parts)

    def _build_prompt(self, question: str, chunks: list[RetrievedChunk]) -> str:
        context = self._format_context(chunks)
        return self._prompt_template.format(context=context, question=question)

    def _should_unknown(self, chunks: list[RetrievedChunk], question: str) -> bool:
        if not chunks:
            return True
        best = max(chunks, key=lambda c: c.score)
        if best.score < self.score_threshold:
            return True
        # mock 模式：明显无关 query（无关键词重叠）
        q_tokens = set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z0-9-]+", question.lower()))
        if not q_tokens:
            return best.score < self.score_threshold
        unrelated_markers = ("天气", "足球", "股票", "比特币")
        if any(m in question for m in unrelated_markers):
            context_text = " ".join(c.content for c in chunks)
            if not any(m in context_text for m in unrelated_markers):
                return True
        return False

    def _mock_generate(self, question: str, chunks: list[RetrievedChunk]) -> str:
        """无 API Key 时基于检索片段拼装回答。"""
        lines: list[str] = []
        if "退款" in question or "退钱" in question:
            for ch in chunks:
                if "退款" in ch.content:
                    for line in ch.content.splitlines():
                        if line.strip():
                            lines.append(line.strip())
                    break
        elif "工单" in question:
            for ch in chunks:
                if "工单" in ch.content:
                    lines.append(ch.content.strip()[:200])
                    break
        elif "大模型" in question.lower() or "llm" in question.lower():
            for ch in chunks:
                if "大模型" in ch.content:
                    lines.append(ch.content.strip()[:220])
                    break
        else:
            lines.append(chunks[0].content.strip()[:240])

        body = "\n".join(f"{i + 1}. {ln}" for i, ln in enumerate(lines[:5])) if lines else chunks[0].content[:200]
        cites = sorted({ch.source for ch in chunks[:3]})
        cite_str = " ".join(f"[{c}]" for c in cites)
        return f"{body}\n\n引用：{cite_str}"

    def _live_generate(self, prompt: str) -> str:
        if requests is None:  # pragma: no cover
            raise RuntimeError("需要 requests")
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        base_url = os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        model = os.getenv("OPENAI_CHAT_MODEL", DEFAULT_CHAT_MODEL)
        resp = requests.post(
            f"{base_url}/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=90,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    def generate(self, question: str, k: int = 4) -> RAGAnswer:
        """retrieve → generate（含 citations / unknown fallback）"""
        chunks = self.retrieve(question, k=k)
        citations = sorted({ch.source for ch in chunks})

        if self._should_unknown(chunks, question):
            return RAGAnswer(
                question=question,
                answer=UNKNOWN_REPLY,
                citations=[],
                chunks=chunks,
                mode=self.mode,
                used_llm=False,
                fallback_unknown=True,
            )

        if self.mode == "mock":
            answer = self._mock_generate(question, chunks)
            return RAGAnswer(
                question=question,
                answer=answer,
                citations=citations,
                chunks=chunks,
                mode=self.mode,
                used_llm=False,
                fallback_unknown=False,
            )

        prompt = self._build_prompt(question, chunks)
        answer = self._live_generate(prompt)
        if "我不知道" in answer and "建议联系" in answer:
            return RAGAnswer(
                question=question,
                answer=UNKNOWN_REPLY,
                citations=[],
                chunks=chunks,
                mode=self.mode,
                used_llm=True,
                fallback_unknown=True,
            )
        return RAGAnswer(
            question=question,
            answer=answer,
            citations=citations,
            chunks=chunks,
            mode=self.mode,
            used_llm=True,
            fallback_unknown=False,
        )

    def ask(self, question: str, k: int = 4) -> RAGAnswer:
        """对外统一入口：确保已 ingest。"""
        if self._store is None or self._get_store()._collection.count() == 0:  # noqa: SLF001
            self.ingest(reset=True)
        return self.generate(question, k=k)


def demo() -> None:
    pipeline = RAGPipeline()
    n = pipeline.ingest(reset=True)
    print(f"ingested chunks={n} mode={pipeline.mode}")

    for q in ["如何申请退款？", "今天北京天气怎么样？"]:
        result = pipeline.generate(q)
        print(f"\nQ: {q}")
        print(f"A: {result.answer[:300]}...")
        print(f"unknown={result.fallback_unknown} citations={result.citations}")


if __name__ == "__main__":
    demo()
