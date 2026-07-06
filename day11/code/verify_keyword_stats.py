# -*- coding: utf-8 -*-
"""
Day 11 关键词统计工具验收脚本。
运行：cd day11/code && python3 verify_keyword_stats.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent

from doc_keyword_stats import (  # noqa: E402
    iter_text_files,
    load_keywords,
    read_document,
    save_report,
    scan_documents,
)


def check_load_keywords() -> None:
    kw_path = CODE_DIR / "data" / "keywords.txt"
    keywords = load_keywords(kw_path)
    assert "退款" in keywords
    assert "大模型" in keywords
    assert len(keywords) >= 4
    print("[OK] load_keywords")


def check_iter_text_files() -> None:
    docs_dir = CODE_DIR / "data" / "sample_docs"
    files = iter_text_files(docs_dir)
    assert len(files) >= 4
    suffixes = {p.suffix.lower() for p in files}
    assert ".txt" in suffixes
    assert ".md" in suffixes
    print("[OK] iter_text_files")


def check_scan_documents() -> None:
    docs_dir = CODE_DIR / "data" / "sample_docs"
    keywords = load_keywords(CODE_DIR / "data" / "keywords.txt")
    report = scan_documents(docs_dir, keywords)

    assert report["total_files"] >= 4
    assert report["summary"]["退款"] > 0
    assert report["summary"]["大模型"] > 0
    assert report["summary"]["工单"] > 0
    assert "scanned_at" in report
    assert len(report["documents"]) == report["total_files"]

    for doc in report["documents"]:
        assert doc["error"] is None, doc
        assert doc["char_count"] > 0

    print("[OK] scan_documents")


def check_save_report() -> None:
    docs_dir = CODE_DIR / "data" / "sample_docs"
    keywords = ["退款", "大模型"]
    report = scan_documents(docs_dir, keywords)

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        out_path = save_report(report, out_dir)
        assert out_path.exists()
        with open(out_path, encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded["summary"]["退款"] == report["summary"]["退款"]
        raw = json.dumps(loaded, ensure_ascii=False)
        assert "退款" in raw
        assert "\\u" not in raw

    print("[OK] save_report")


def check_read_document_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.bin"
        bad.write_bytes(b"\xff\xfe\x00")
        text, error = read_document(bad)
        assert text is None
        assert error is not None

    print("[OK] read_document 错误隔离")


def main() -> None:
    print("Day 11 关键词统计验收")
    print("-" * 40)
    check_load_keywords()
    check_iter_text_files()
    check_scan_documents()
    check_save_report()
    check_read_document_error()
    print("-" * 40)
    print("全部通过 ✓")


if __name__ == "__main__":
    main()
