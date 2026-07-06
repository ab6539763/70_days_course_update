# -*- coding: utf-8 -*-
"""
Day 30 · RAG 命令行工具（KEY DAY）

子命令：
  ingest   — 重建向量库
  ask      — 单次问答
  chat     — 交互式多轮（每轮独立检索）

运行：cd day30/code && python3 rag_cli.py ask "如何申请退款？"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from rag_pipeline import RAGPipeline, UNKNOWN_REPLY  # noqa: E402


def cmd_ingest(args: argparse.Namespace) -> int:
    pipeline = RAGPipeline(score_threshold=args.threshold)
    docs_dir = Path(args.docs_dir) if args.docs_dir else None
    n = pipeline.ingest(
        docs_dir=docs_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.overlap,
        reset=not args.no_reset,
    )
    print(json.dumps({"chunks": n, "mode": pipeline.mode, "persist": str(pipeline.persist_directory)}, ensure_ascii=False))
    return 0


def _print_answer(result) -> None:
    print("\n" + "=" * 60)
    print(f"问题: {result.question}")
    print("-" * 60)
    print(result.answer)
    print("-" * 60)
    if result.citations:
        print("引用:", ", ".join(result.citations))
    if result.fallback_unknown:
        print(f"[兜底] {UNKNOWN_REPLY}")
    print(f"mode={result.mode} chunks_used={len(result.chunks)}")
    for i, ch in enumerate(result.chunks[:3]):
        print(f"  检索#{i} score={ch.score:.3f} source={ch.source}")
    print("=" * 60 + "\n")


def cmd_ask(args: argparse.Namespace) -> int:
    os.environ.setdefault("SPARKTECH_MOCK", "1" if args.mock else os.getenv("SPARKTECH_MOCK", "1"))
    pipeline = RAGPipeline(score_threshold=args.threshold)
    if args.rebuild:
        pipeline.ingest(reset=True)
    result = pipeline.ask(args.question, k=args.top_k)
    if args.json:
        payload = {
            "question": result.question,
            "answer": result.answer,
            "citations": result.citations,
            "fallback_unknown": result.fallback_unknown,
            "mode": result.mode,
            "chunks": [
                {"source": c.source, "score": round(c.score, 4), "preview": c.content[:100]}
                for c in result.chunks
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_answer(result)
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    os.environ.setdefault("SPARKTECH_MOCK", "1" if args.mock else os.getenv("SPARKTECH_MOCK", "1"))
    pipeline = RAGPipeline(score_threshold=args.threshold)
    pipeline.ingest(reset=True)
    print("星火智服 RAG CLI · 输入 exit 退出")
    while True:
        try:
            question = input("\n你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("再见。")
            break
        result = pipeline.generate(question, k=args.top_k)
        _print_answer(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Day 30 星火智服 RAG CLI")
    parser.add_argument("--mock", action="store_true", help="强制 mock 模式")
    parser.add_argument("--threshold", type=float, default=None, help="检索分数阈值")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="load→split→embed→store")
    p_ingest.add_argument("--docs-dir", default=None)
    p_ingest.add_argument("--chunk-size", type=int, default=400)
    p_ingest.add_argument("--overlap", type=int, default=60)
    p_ingest.add_argument("--no-reset", action="store_true")
    p_ingest.set_defaults(func=cmd_ingest)

    p_ask = sub.add_parser("ask", help="单次问答")
    p_ask.add_argument("question", help="用户问题")
    p_ask.add_argument("--top-k", type=int, default=4)
    p_ask.add_argument("--rebuild", action="store_true", help="问答前重建索引")
    p_ask.add_argument("--json", action="store_true", help="JSON 输出")
    p_ask.set_defaults(func=cmd_ask)

    p_chat = sub.add_parser("chat", help="交互式问答")
    p_chat.add_argument("--top-k", type=int, default=4)
    p_chat.set_defaults(func=cmd_chat)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
