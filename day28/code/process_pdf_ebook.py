# -*- coding: utf-8 -*-
"""
Day 28 · PDF 电子书处理流水线

load(PDF) → split(RecursiveCharacterTextSplitter) → 导出 JSON 切块清单

运行：cd day28/code && python3 process_pdf_ebook.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = CODE_DIR / "data" / "sample_docs"
OUTPUT_DIR = CODE_DIR / "output"
sys.path.insert(0, str(CODE_DIR))

from ensure_samples import ensure_sample_pdf  # noqa: E402
from langchain_text_splitters import RecursiveCharacterTextSplitter

from doc_loader_demo import load_pdf, load_txt  # noqa: E402


@dataclass
class ChunkRecord:
    chunk_id: int
    chars: int
    source: str
    page: int | None
    preview: str


@dataclass
class EbookProcessResult:
    source_file: str
    total_chars: int
    chunk_size: int
    chunk_overlap: int
    num_chunks: int
    chunks: list[ChunkRecord]
    processed_at: str


def load_ebook_documents(pdf_path: Path):
    """加载 PDF；若文本过少则回退到同名 .pdf.txt。"""
    docs = load_pdf(pdf_path)
    total_chars = sum(len(d.page_content) for d in docs)
    if total_chars < 50:
        fallback = pdf_path.with_suffix(".pdf.txt")
        if fallback.is_file():
            print(f"[INFO] PDF 文本过少，回退读取 {fallback.name}")
            docs = load_txt(fallback)
    return docs


def process_ebook(
    pdf_path: Path | None = None,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> EbookProcessResult:
    pdf_path = pdf_path or ensure_sample_pdf()
    docs = load_ebook_documents(pdf_path)
    total_chars = sum(len(d.page_content) for d in docs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    records: list[ChunkRecord] = []
    for i, chunk in enumerate(chunks):
        records.append(
            ChunkRecord(
                chunk_id=i,
                chars=len(chunk.page_content),
                source=str(chunk.metadata.get("source", pdf_path)),
                page=chunk.metadata.get("page"),
                preview=chunk.page_content.replace("\n", " ")[:100],
            )
        )

    return EbookProcessResult(
        source_file=str(pdf_path),
        total_chars=total_chars,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        num_chunks=len(records),
        chunks=records,
        processed_at=datetime.now(timezone.utc).isoformat(),
    )


def save_result(result: EbookProcessResult) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"ebook_chunks_{ts}.json"
    path.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    print("Day 28 · process_pdf_ebook.py")
    result = process_ebook()
    out = save_result(result)

    print(f"源文件: {result.source_file}")
    print(f"总字符: {result.total_chars}")
    print(f"切块参数: size={result.chunk_size} overlap={result.chunk_overlap}")
    print(f"块数: {result.num_chunks}")
    print("\n前 3 块预览:")
    for rec in result.chunks[:3]:
        print(f"  #{rec.chunk_id} page={rec.page} chars={rec.chars}")
        print(f"      {rec.preview}...")
    print(f"\n[OK] 已导出 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
