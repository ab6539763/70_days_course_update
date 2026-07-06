# -*- coding: utf-8 -*-
"""
Day 29 · 相似检索演示

构建向量库后对多条 query 做 similarity_search_with_score。

运行：cd day29/code && python3 similarity_search_demo.py
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from build_vectorstore import build_vectorstore, save_report
from chroma_kb import ChromaKnowledgeBase

CODE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = CODE_DIR / "output"

DEMO_QUERIES = [
    "如何申请退款？",
    "大模型 Token 能退吗？",
    "工单多久回复？",
    "星火智服是什么？",
    "订单 ST-10002 状态",  # CSV 相关
    "今天北京天气怎么样？",  # 应无高相关块
]


@dataclass
class QueryResult:
    query: str
    hits: list[dict]


def run_demo(kb: ChromaKnowledgeBase | None = None) -> list[QueryResult]:
    if kb is None:
        kb, _ = build_vectorstore(reset=True)

    results: list[QueryResult] = []
    print(f"向量库文档数: {kb.count()}  mode={kb.mode}\n")

    for query in DEMO_QUERIES:
        hits = kb.similarity_search_with_score(query, k=3)
        print(f"Q: {query}")
        hit_dicts = []
        for i, hit in enumerate(hits):
            print(f"  #{i} score={hit.score:.4f} [{hit.source_label()}]")
            print(f"      {hit.content.replace(chr(10), ' ')[:90]}...")
            hit_dicts.append(
                {
                    "score": round(hit.score, 4),
                    "source": hit.source_label(),
                    "preview": hit.content[:120],
                }
            )
        results.append(QueryResult(query=query, hits=hit_dicts))
        print()

    return results


def save_results(results: list[QueryResult]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"similarity_demo_{ts}.json"
    payload = [asdict(r) for r in results]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    print("Day 29 · similarity_search_demo.py")
    results = run_demo()
    out = save_results(results)
    print(f"[OK] 结果已写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
