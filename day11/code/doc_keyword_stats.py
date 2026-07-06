# -*- coding: utf-8 -*-
"""
星火智服 · 批量文档关键词统计 CLI（RAG 文档处理前奏）。

运行：
    cd day11/code
    python3 doc_keyword_stats.py
    python3 doc_keyword_stats.py -d data/sample_docs -k data/keywords.txt -o output
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

CODE_DIR = Path(__file__).resolve().parent
DEFAULT_DOCS_DIR = CODE_DIR / "data" / "sample_docs"
DEFAULT_KEYWORDS = CODE_DIR / "data" / "keywords.txt"
DEFAULT_OUTPUT_DIR = CODE_DIR / "output"

TEXT_SUFFIXES = {".txt", ".md"}


def load_keywords(path: Path) -> list[str]:
    """从文本文件加载关键词，每行一词，支持 # 注释。"""
    if not path.is_file():
        raise FileNotFoundError(f"关键词文件不存在: {path}")

    keywords: list[str] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            keywords.append(line)
    if not keywords:
        raise ValueError(f"关键词文件为空: {path}")
    return keywords


def iter_text_files(root: Path) -> list[Path]:
    """递归收集 root 下所有 .txt / .md 文件。"""
    if not root.is_dir():
        raise NotADirectoryError(f"文档目录不存在: {root}")

    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return files


def read_document(path: Path) -> tuple[str | None, str | None]:
    """读取单个文档；成功返回 (text, None)，失败返回 (None, error_msg)。"""
    try:
        text = path.read_text(encoding="utf-8")
        return text, None
    except OSError as exc:
        return None, f"读取失败: {exc}"
    except UnicodeDecodeError as exc:
        return None, f"编码错误（需 UTF-8）: {exc}"


def count_keyword(text: str, keyword: str, *, case_sensitive: bool = False) -> int:
    """统计关键词在文本中的出现次数（子串匹配）。"""
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.escape(keyword)
    return len(re.findall(pattern, text, flags))


def scan_documents(
    docs_dir: Path,
    keywords: list[str],
    *,
    case_sensitive: bool = False,
) -> dict[str, Any]:
    """扫描目录下所有文本文档，返回统计报告字典。"""
    docs_dir = docs_dir.resolve()
    files = iter_text_files(docs_dir)

    summary: dict[str, int] = {kw: 0 for kw in keywords}
    documents: list[dict[str, Any]] = []

    for path in files:
        rel = str(path.relative_to(docs_dir))
        text, error = read_document(path)

        if error:
            documents.append(
                {
                    "path": rel,
                    "char_count": 0,
                    "hits": {},
                    "error": error,
                }
            )
            continue

        hits: dict[str, int] = {}
        for kw in keywords:
            n = count_keyword(text, kw, case_sensitive=case_sensitive)
            hits[kw] = n
            summary[kw] += n

        documents.append(
            {
                "path": rel,
                "char_count": len(text),
                "hits": hits,
                "error": None,
            }
        )

    return {
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "docs_dir": str(docs_dir),
        "total_files": len(files),
        "keywords": keywords,
        "summary": summary,
        "documents": documents,
    }


def save_report(report: dict[str, Any], output_dir: Path) -> Path:
    """将报告写入带时间戳的 JSON 文件。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"keyword_report_{stamp}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return out_path


def print_summary(report: dict[str, Any], out_path: Path) -> None:
    """打印控制台摘要。"""
    print("星火智服 · 文档关键词统计")
    print("-" * 40)
    print(f"扫描时间:   {report['scanned_at']}")
    print(f"文档目录:   {report['docs_dir']}")
    print(f"文件总数:   {report['total_files']}")
    print(f"关键词:     {', '.join(report['keywords'])}")
    print("-" * 40)
    print("汇总命中:")
    for kw, count in report["summary"].items():
        print(f"  {kw}: {count}")
    print("-" * 40)
    errors = [d for d in report["documents"] if d.get("error")]
    if errors:
        print(f"读失败文件: {len(errors)} 个")
        for doc in errors:
            print(f"  ✗ {doc['path']}: {doc['error']}")
    print(f"报告已保存: {out_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="批量扫描 txt/md 文档并统计关键词命中次数",
    )
    parser.add_argument(
        "-d",
        "--docs-dir",
        type=Path,
        default=DEFAULT_DOCS_DIR,
        help="文档根目录（默认: data/sample_docs）",
    )
    parser.add_argument(
        "-k",
        "--keywords",
        type=Path,
        default=DEFAULT_KEYWORDS,
        help="关键词文件，每行一词（默认: data/keywords.txt）",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="JSON 报告输出目录（默认: output）",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="区分英文大小写（默认忽略）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    keywords = load_keywords(args.keywords)
    report = scan_documents(
        args.docs_dir,
        keywords,
        case_sensitive=args.case_sensitive,
    )
    out_path = save_report(report, args.output_dir)
    print_summary(report, out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
