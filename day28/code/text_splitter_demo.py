# -*- coding: utf-8 -*-
"""
Day 28 · Text Splitter 演示

对比 CharacterTextSplitter 与 RecursiveCharacterTextSplitter，
并演示 chunk_size / chunk_overlap 调参对块数与预览的影响。

运行：cd day28/code && python3 text_splitter_demo.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = CODE_DIR / "data" / "sample_docs"
OUTPUT_DIR = CODE_DIR / "output"
sys.path.insert(0, str(CODE_DIR))

from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

from doc_loader_demo import load_markdown, load_txt  # noqa: E402


@dataclass
class SplitReport:
    splitter: str
    chunk_size: int
    chunk_overlap: int
    num_chunks: int
    avg_len: float
    min_len: int
    max_len: int
    first_preview: str


def load_long_corpus() -> str:
    """合并多篇样本为较长语料，便于观察切块差异。"""
    parts: list[str] = []
    for path in [
        SAMPLE_DIR / "llm_intro.md",
        SAMPLE_DIR / "service_policy.txt",
        SAMPLE_DIR / "faq_refund.txt",
    ]:
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def split_with(
    text: str,
    splitter_name: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Document]:
    if splitter_name == "character":
        splitter = CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator="\n",
        )
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
        )
    return splitter.split_documents([Document(page_content=text, metadata={"source": "corpus"})])


def make_report(chunks: list[Document], splitter: str, chunk_size: int, overlap: int) -> SplitReport:
    lengths = [len(c.page_content) for c in chunks]
    avg_len = sum(lengths) / len(lengths) if lengths else 0.0
    preview = chunks[0].page_content.replace("\n", " ")[:80] if chunks else ""
    return SplitReport(
        splitter=splitter,
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        num_chunks=len(chunks),
        avg_len=round(avg_len, 1),
        min_len=min(lengths) if lengths else 0,
        max_len=max(lengths) if lengths else 0,
        first_preview=preview,
    )


def print_report(report: SplitReport) -> None:
    print(
        f"  {report.splitter:12} size={report.chunk_size:4} overlap={report.chunk_overlap:3} "
        f"-> chunks={report.num_chunks:3} avg={report.avg_len:6.1f} "
        f"min={report.min_len:4} max={report.max_len:4}"
    )
    print(f"      first: {report.first_preview}...")


def tune_chunk_size_demo(text: str) -> list[SplitReport]:
    print("\n--- chunk_size 调参（RecursiveCharacterTextSplitter, overlap=50）---")
    reports: list[SplitReport] = []
    for size in (100, 200, 400, 800):
        chunks = split_with(text, "recursive", size, 50)
        report = make_report(chunks, "recursive", size, 50)
        reports.append(report)
        print_report(report)
    return reports


def compare_splitters(text: str) -> list[SplitReport]:
    print("\n--- Character vs Recursive（chunk_size=300, overlap=30）---")
    reports: list[SplitReport] = []
    for name in ("character", "recursive"):
        chunks = split_with(text, name, 300, 30)
        report = make_report(chunks, name, 300, 30)
        reports.append(report)
        print_report(report)
    return reports


def demo_metadata_preserved() -> None:
    print("\n--- 单文件加载后切块（保留 metadata.source）---")
    docs = load_markdown(SAMPLE_DIR / "product_guide.md")
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    chunks = splitter.split_documents(docs)
    for i, c in enumerate(chunks[:2]):
        print(f"  chunk#{i} source={c.metadata.get('source')} len={len(c.page_content)}")


def save_reports(reports: list[SplitReport], filename: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(
        json.dumps([asdict(r) for r in reports], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def main() -> int:
    print("Day 28 · text_splitter_demo.py")
    corpus = load_long_corpus()
    print(f"语料总字符数: {len(corpus)}")

    reports = compare_splitters(corpus)
    reports.extend(tune_chunk_size_demo(corpus))
    demo_metadata_preserved()

    out_path = save_reports(reports, "splitter_tuning_report.json")
    print(f"\n[OK] 调参报告已写入 {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
