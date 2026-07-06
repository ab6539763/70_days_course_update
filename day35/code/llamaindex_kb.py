# -*- coding: utf-8 -*-
"""
Day 35 · LlamaIndex 知识库问答

- live 模式：llama-index 已安装时使用 SimpleDirectoryReader + VectorStoreIndex
- mock 模式：无 llama-index / 无 API Key 时使用轻量检索 + 模板回答

用法：
  python3 llamaindex_kb.py
  python3 llamaindex_kb.py --question "如何申请退款？"
  python3 llamaindex_kb.py --repl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

CODE_DIR = Path(__file__).resolve().parent
DATA_DIR = CODE_DIR / "data" / "kb_docs"
DEFAULT_TOP_K = 3

# LlamaIndex 可选依赖
HAS_LLAMAINDEX = False
LLAMAINDEX_ERROR = ""

try:
    from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.readers import SimpleDirectoryReader

    HAS_LLAMAINDEX = True
except ImportError as exc:  # pragma: no cover
    LLAMAINDEX_ERROR = str(exc)


def load_dotenv_file() -> None:
    if load_dotenv is None:
        return
    for candidate in (CODE_DIR / ".env", CODE_DIR.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()


def tokenize(text: str) -> set[str]:
    text = text.lower()
    tokens = set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-z0-9]{2,}", text))
    han = re.sub(r"[^\u4e00-\u9fff]", "", text)
    for i in range(len(han) - 1):
        tokens.add(han[i : i + 2])
    return tokens


def jaccard(a: str, b: str) -> float:
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


@dataclass
class RetrievedChunk:
    text: str
    score: float
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryResult:
    question: str
    answer: str
    chunks: list[RetrievedChunk]
    engine: str
    mode: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "engine": self.engine,
            "mode": self.mode,
            "chunks": [
                {
                    "text": c.text,
                    "score": round(c.score, 4),
                    "source": c.source,
                    "metadata": c.metadata,
                }
                for c in self.chunks
            ],
        }


class MockKBEngine:
    """无 LlamaIndex 时的教学版知识库引擎。"""

    def __init__(self, data_dir: Path, chunk_size: int = 200) -> None:
        self.data_dir = data_dir
        self.chunk_size = chunk_size
        self.chunks: list[RetrievedChunk] = []

    def load(self) -> int:
        self.chunks.clear()
        for path in sorted(self.data_dir.glob("**/*")):
            if path.suffix.lower() not in {".md", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8")
            for piece in self._split_markdown(text):
                self.chunks.append(
                    RetrievedChunk(
                        text=piece,
                        score=0.0,
                        source=str(path.relative_to(self.data_dir)),
                        metadata={},
                    )
                )
        return len(self.chunks)

    def _split_markdown(self, text: str) -> list[str]:
        """按 ## 章节切分，每节独立成块便于检索。"""
        sections: list[str] = []
        current: list[str] = []
        for line in text.splitlines():
            if line.startswith("## "):
                if current:
                    sections.append("\n".join(current).strip())
                current = [line[3:].strip(), ""]
            else:
                current.append(line)
        if current:
            sections.append("\n".join(current).strip())
        if not sections:
            return self._split_text(text)
        return [s for s in sections if len(s) > 10]

    def _split_text(self, text: str) -> list[str]:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        pieces: list[str] = []
        buf = ""
        for para in paragraphs:
            if len(buf) + len(para) <= self.chunk_size:
                buf = f"{buf}\n{para}".strip()
            else:
                if buf:
                    pieces.append(buf)
                buf = para
        if buf:
            pieces.append(buf)
        return pieces

    def retrieve(self, question: str, top_k: int = DEFAULT_TOP_K) -> list[RetrievedChunk]:
        scored: list[RetrievedChunk] = []
        for chunk in self.chunks:
            score = jaccard(question, chunk.text)
            scored.append(
                RetrievedChunk(
                    text=chunk.text,
                    score=score,
                    source=chunk.source,
                    metadata=chunk.metadata,
                )
            )
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:top_k]

    def query(self, question: str, top_k: int = DEFAULT_TOP_K) -> QueryResult:
        hits = self.retrieve(question, top_k=top_k)
        answer = self._synthesize_answer(question, hits)
        return QueryResult(
            question=question,
            answer=answer,
            chunks=hits,
            engine="mock_kb",
            mode="mock",
        )

    def _clean_chunk_text(self, text: str) -> str:
        parts: list[str] = []
        for line in text.splitlines():
            line = re.sub(r"^#+\s*", "", line).strip()
            line = re.sub(r"^[-*]\s+", "", line)
            if line:
                parts.append(line)
        return " ".join(parts)

    def _synthesize_answer(self, question: str, hits: list[RetrievedChunk]) -> str:
        if not hits or hits[0].score < 0.03:
            return "抱歉，知识库中未找到相关信息，建议转人工客服。"

        for hit in hits:
            body = self._clean_chunk_text(hit.text)
            if len(body) < 12:
                continue
            for sep in ("。", "；", "!", "?"):
                if sep in body:
                    sentence = body.split(sep)[0].strip()
                    if len(sentence) >= 8:
                        return f"{sentence}。（来源：{hit.source}）"
            preview = body[:100] + ("..." if len(body) > 100 else "")
            return f"{preview}（来源：{hit.source}）"

        return "抱歉，知识库中未找到相关信息，建议转人工客服。"


class LlamaIndexKBEngine:
    """LlamaIndex 封装：DirectoryReader → VectorStoreIndex → QueryEngine。"""

    def __init__(self, data_dir: Path, top_k: int = DEFAULT_TOP_K) -> None:
        self.data_dir = data_dir
        self.top_k = top_k
        self._query_engine = None
        self._index = None

    def load(self) -> int:
        if not HAS_LLAMAINDEX:
            raise RuntimeError(f"llama-index 未安装: {LLAMAINDEX_ERROR}")

        # 课堂默认：无 embedding API 时用 mock embedding
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return self._load_with_mock_embedding()

        try:
            from llama_index.embeddings.openai import OpenAIEmbedding
            from llama_index.llms.openai import OpenAI

            Settings.llm = OpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                api_key=api_key,
                api_base=os.getenv("OPENAI_BASE_URL"),
            )
            Settings.embed_model = OpenAIEmbedding(
                model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
                api_key=api_key,
                api_base=os.getenv("OPENAI_BASE_URL"),
            )
            mode = "live"
        except ImportError:
            return self._load_with_mock_embedding()

        documents = SimpleDirectoryReader(str(self.data_dir)).load_data()
        splitter = SentenceSplitter(chunk_size=256, chunk_overlap=32)
        nodes = splitter.get_nodes_from_documents(documents)
        self._index = VectorStoreIndex(nodes)
        self._query_engine = self._index.as_query_engine(similarity_top_k=self.top_k)
        self._mode = mode
        return len(nodes)

    def _load_with_mock_embedding(self) -> int:
        """使用确定性 mock embedding，无需 API Key。"""
        from llama_index.core.embeddings import BaseEmbedding

        class MockEmbedding(BaseEmbedding):
            def _get_text_embedding(self, text: str) -> list[float]:
                return _mock_embed(text)

            async def _aget_text_embedding(self, text: str) -> list[float]:
                return self._get_text_embedding(text)

            def _get_query_embedding(self, query: str) -> list[float]:
                return self._get_text_embedding(query)

            async def _aget_query_embedding(self, query: str) -> list[float]:
                return self._get_query_embedding(query)

        Settings.embed_model = MockEmbedding(embed_dim=64)
        Settings.llm = None  # 检索后本地拼答案

        documents = SimpleDirectoryReader(str(self.data_dir)).load_data()
        splitter = SentenceSplitter(chunk_size=256, chunk_overlap=32)
        nodes = splitter.get_nodes_from_documents(documents)
        self._index = VectorStoreIndex(nodes)
        self._query_engine = self._index.as_retriever(similarity_top_k=self.top_k)
        self._mode = "llamaindex_mock_embed"
        return len(nodes)

    def retrieve(self, question: str, top_k: int | None = None) -> list[RetrievedChunk]:
        k = top_k or self.top_k
        if self._query_engine is None:
            raise RuntimeError("请先调用 load()")

        if hasattr(self._query_engine, "retrieve"):
            nodes = self._query_engine.retrieve(question)
        else:
            response = self._query_engine.query(question)
            return [
                RetrievedChunk(
                    text=str(response),
                    score=1.0,
                    source="query_engine",
                    metadata={},
                )
            ]

        chunks: list[RetrievedChunk] = []
        for node in nodes[:k]:
            text = node.get_content()
            score = float(getattr(node, "score", 0.0) or 0.0)
            source = node.metadata.get("file_name", "unknown")
            chunks.append(RetrievedChunk(text=text, score=score, source=source, metadata=node.metadata))
        return chunks

    def query(self, question: str, top_k: int | None = None) -> QueryResult:
        k = top_k or self.top_k
        if getattr(self, "_mode", "") == "llamaindex_mock_embed" or Settings.llm is None:
            hits = self.retrieve(question, top_k=k)
            synthesizer = MockKBEngine(self.data_dir)
            answer = synthesizer._synthesize_answer(question, hits)
            return QueryResult(
                question=question,
                answer=answer,
                chunks=hits,
                engine="llamaindex",
                mode=getattr(self, "_mode", "mock"),
            )

        response = self._query_engine.query(question)
        source_nodes = getattr(response, "source_nodes", []) or []
        chunks = [
            RetrievedChunk(
                text=n.get_content(),
                score=float(getattr(n, "score", 0.0) or 0.0),
                source=n.metadata.get("file_name", "unknown"),
                metadata=n.metadata,
            )
            for n in source_nodes[:k]
        ]
        return QueryResult(
            question=question,
            answer=str(response),
            chunks=chunks,
            engine="llamaindex",
            mode=self._mode,
        )


def _mock_embed(text: str, dim: int = 64) -> list[float]:
    vec = [0.0] * dim
    for token in tokenize(text):
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0 if (h >> 3) % 2 == 0 else -1.0
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]


def create_kb_engine(
    data_dir: Path | None = None,
    force_mock: bool = False,
) -> MockKBEngine | LlamaIndexKBEngine:
    data_dir = data_dir or DATA_DIR
    use_llamaindex = HAS_LLAMAINDEX and not force_mock
    if os.getenv("LLAMAINDEX_FORCE_MOCK", "").strip() in {"1", "true", "yes"}:
        use_llamaindex = False

    if use_llamaindex:
        return LlamaIndexKBEngine(data_dir)
    return MockKBEngine(data_dir)


def format_result(result: QueryResult) -> str:
    lines = [
        f"问题：{result.question}",
        f"引擎：{result.engine} ({result.mode})",
        "-" * 48,
        f"回答：{result.answer}",
        "",
        "检索片段：",
    ]
    for i, chunk in enumerate(result.chunks, 1):
        preview = chunk.text.replace("\n", " ")[:80]
        lines.append(f"  [{i}] score={chunk.score:.4f} src={chunk.source}")
        lines.append(f"      {preview}{'...' if len(chunk.text) > 80 else ''}")
    return "\n".join(lines)


def demo_questions() -> list[str]:
    return [
        "如何申请退款？",
        "忘记密码怎么办？",
        "星火智服支持哪些大模型？",
    ]


def run_repl(engine: MockKBEngine | LlamaIndexKBEngine) -> None:
    print("进入知识库问答 REPL，输入 /exit 退出")
    while True:
        try:
            question = input("\n你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break
        if not question:
            continue
        if question.lower() in {"/exit", "exit", "quit"}:
            print("再见。")
            break
        result = engine.query(question)
        print(format_result(result))


def main() -> int:
    load_dotenv_file()
    parser = argparse.ArgumentParser(description="Day 35 LlamaIndex 知识库问答")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--question", "-q", type=str, default="")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--force-mock", action="store_true")
    parser.add_argument("--repl", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    engine = create_kb_engine(args.data_dir, force_mock=args.force_mock)
    count = engine.load()
    print(f"[llamaindex_kb] 已加载 {count} 个索引单元，引擎={engine.__class__.__name__}")

    if args.repl:
        run_repl(engine)
        return 0

    questions = [args.question] if args.question else demo_questions()
    results: list[dict[str, Any]] = []
    for q in questions:
        result = engine.query(q, top_k=args.top_k)
        results.append(result.to_dict())
        if not args.json:
            print("\n" + "=" * 56)
            print(format_result(result))

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
