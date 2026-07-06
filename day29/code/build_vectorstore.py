# -*- coding: utf-8 -*-
"""
Day 29 · 从 Day 28 样本文档构建 Chroma 向量库

load → split → embed → persist

运行：cd day29/code && python3 build_vectorstore.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chroma_kb import ChromaKnowledgeBase, DEFAULT_COLLECTION
from mock_embeddings import get_embeddings, is_mock_mode

CODE_DIR = Path(__file__).resolve().parent
WORKSPACE = CODE_DIR.parents[1]
DAY28_DOCS = WORKSPACE / "day28" / "code" / "data" / "sample_docs"
LOCAL_DOCS = CODE_DIR / "data" / "sample_docs"
OUTPUT_DIR = CODE_DIR / "output"


@dataclass
class BuildReport:
    docs_dir: str
    files_loaded: int
    raw_documents: int
    chunks: int
    collection: str
    persist_dir: str
    embedding_mode: str
    chunk_size: int
    chunk_overlap: int
    built_at: str


def resolve_docs_dir() -> Path:
    if DAY28_DOCS.is_dir():
        return DAY28_DOCS
    if LOCAL_DOCS.is_dir():
        return LOCAL_DOCS
    raise FileNotFoundError("未找到 sample_docs，请先完成 Day 28 或复制样本到 day29/code/data/sample_docs")


def load_text_file(path: Path) -> Document:
    text = path.read_text(encoding="utf-8")
    return Document(page_content=text, metadata={"source": str(path), "format": path.suffix.lstrip(".")})


def load_all_documents(docs_dir: Path) -> list[Document]:
    """加载 txt/md/csv/html；PDF/Word 若存在则尝试 LangChain Loader。"""
    docs: list[Document] = []
    patterns = ["*.txt", "*.md", "*.csv", "*.html"]

    for pattern in patterns:
        for path in sorted(docs_dir.glob(pattern)):
            if path.suffix.lower() == ".csv":
                from langchain_community.document_loaders import CSVLoader

                loader = CSVLoader(str(path), encoding="utf-8")
                docs.extend(loader.load())
            elif path.suffix.lower() == ".html":
                from langchain_community.document_loaders import BSHTMLLoader

                loader = BSHTMLLoader(str(path), open_encoding="utf-8")
                docs.extend(loader.load())
            else:
                docs.extend([load_text_file(path)])

    pdf_path = docs_dir / "ebook.pdf"
    if pdf_path.is_file():
        try:
            from langchain_community.document_loaders import PyPDFLoader

            docs.extend(PyPDFLoader(str(pdf_path)).load())
        except Exception as exc:
            print(f"[WARN] PDF 加载失败: {exc}")

    docx_path = docs_dir / "policy.docx"
    if docx_path.is_file():
        try:
            from docx import Document as DocxDocument

            docx = DocxDocument(str(docx_path))
            text = "\n".join(p.text for p in docx.paragraphs if p.text.strip())
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": str(docx_path), "format": "docx"},
                )
            )
        except Exception as exc:
            print(f"[WARN] DOCX 加载失败: {exc}")

    return docs


def split_documents(
    docs: list[Document],
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )
    return splitter.split_documents(docs)


def build_vectorstore(
    docs_dir: Path | None = None,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
    reset: bool = True,
) -> tuple[ChromaKnowledgeBase, BuildReport]:
    docs_dir = docs_dir or resolve_docs_dir()
    raw_docs = load_all_documents(docs_dir)
    chunks = split_documents(raw_docs, chunk_size, chunk_overlap)

    kb = ChromaKnowledgeBase(embedding=get_embeddings())
    if reset:
        kb.reset()
    kb.add_documents(chunks)

    file_count = len(list(docs_dir.glob("*")))
    report = BuildReport(
        docs_dir=str(docs_dir),
        files_loaded=file_count,
        raw_documents=len(raw_docs),
        chunks=len(chunks),
        collection=DEFAULT_COLLECTION,
        persist_dir=str(kb.persist_directory),
        embedding_mode="mock" if is_mock_mode() else "live",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        built_at=datetime.now(timezone.utc).isoformat(),
    )
    return kb, report


def save_report(report: BuildReport) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"build_report_{ts}.json"
    path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    print("Day 29 · build_vectorstore.py")
    try:
        kb, report = build_vectorstore()
    except FileNotFoundError as exc:
        print(f"[FAIL] {exc}")
        return 1

    out = save_report(report)
    print(f"docs_dir: {report.docs_dir}")
    print(f"raw_documents={report.raw_documents} chunks={report.chunks}")
    print(f"embedding_mode={report.embedding_mode} persist={report.persist_dir}")
    print(f"collection count={kb.count()}")
    print(f"[OK] report -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
