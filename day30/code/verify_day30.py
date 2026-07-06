# -*- coding: utf-8 -*-
"""
Day 30 验收脚本 —— KEY DAY 全链路 RAG

运行：cd day30/code && python3 verify_day30.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ.setdefault("SPARKTECH_MOCK", "1")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_prompt_exists() -> None:
    path = CODE_DIR / "prompts" / "rag_prompt.txt"
    if not path.is_file():
        fail("rag_prompt.txt 缺失")
    text = path.read_text(encoding="utf-8")
    if "{context}" not in text or "{question}" not in text:
        fail("prompt 缺少占位符")
    ok("rag_prompt.txt 模板完整")


def test_ingest_pipeline() -> None:
    from rag_pipeline import RAGPipeline, resolve_docs_dir

    assert resolve_docs_dir().is_dir()
    pipeline = RAGPipeline()
    n = pipeline.ingest(reset=True)
    if n < 5:
        fail(f"ingest 块数过少: {n}")
    ok(f"ingest chunks={n}")


def test_refund_answer() -> None:
    from rag_pipeline import RAGPipeline

    pipeline = RAGPipeline()
    pipeline.ingest(reset=True)
    result = pipeline.generate("如何申请退款？")
    if result.fallback_unknown:
        fail("退款问题不应触发 unknown")
    if "退款" not in result.answer and "工单" not in result.answer:
        fail(f"回答应含退款相关信息: {result.answer[:120]}")
    if not result.citations:
        fail("应有 citations")
    ok(f"退款问答 citations={result.citations}")


def test_unknown_fallback() -> None:
    from rag_pipeline import RAGPipeline, UNKNOWN_REPLY

    pipeline = RAGPipeline()
    pipeline.ingest(reset=True)
    result = pipeline.generate("今天上海比特币足球比赛天气股票怎么样？")
    if not result.fallback_unknown:
        fail("无关问题应触发 unknown fallback")
    if UNKNOWN_REPLY not in result.answer:
        fail(f"应返回标准 unknown 文案: {result.answer}")
    ok("unknown fallback 触发正确")


def test_cli_ask() -> None:
    cmd = [
        sys.executable,
        str(CODE_DIR / "rag_cli.py"),
        "--mock",
        "ask",
        "工单多久回复？",
        "--rebuild",
        "--json",
    ]
    proc = subprocess.run(cmd, cwd=CODE_DIR, capture_output=True, text=True)
    if proc.returncode != 0:
        fail(f"rag_cli 失败: {proc.stderr}")
    if "answer" not in proc.stdout:
        fail("CLI JSON 缺少 answer 字段")
    ok("rag_cli ask --json")


def test_full_chain_labels() -> None:
    """确认模块具备 load/split/embed/store/retrieve/generate 阶段。"""
    import inspect

    from rag_pipeline import RAGPipeline

    methods = {"ingest", "retrieve", "generate", "ask"}
    for name in methods:
        if not hasattr(RAGPipeline, name):
            fail(f"RAGPipeline 缺少 {name}")
    src = inspect.getsource(RAGPipeline.ingest)
    for keyword in ("split", "add_documents"):
        if keyword not in src:
            fail(f"ingest 应包含 {keyword}")
    ok("RAG 六阶段 API 完整")


def main() -> None:
    print("=== Day 30 verify (KEY DAY) ===\n")
    test_prompt_exists()
    test_full_chain_labels()
    test_ingest_pipeline()
    test_refund_answer()
    test_unknown_fallback()
    test_cli_ask()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
