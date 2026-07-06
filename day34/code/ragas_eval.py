# -*- coding: utf-8 -*-
"""
Day 34 · Ragas 评估封装

- 已安装 ragas + datasets：调用官方 evaluate()
- 未安装：回退到 rag_eval_demo 启发式 mock 评估

用法：
  python3 ragas_eval.py
  python3 ragas_eval.py --limit 3
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from rag_eval_demo import (  # noqa: E402
    RAGEvalInput,
    evaluate_rag_sample,
    load_qa_pairs,
    mock_rag_pipeline,
)

DEFAULT_QA_PATH = CODE_DIR / "sample_qa_pairs.json"

# Ragas 可选依赖
HAS_RAGAS = False
RAGAS_IMPORT_ERROR = ""

try:
    from datasets import Dataset
    from ragas import evaluate as ragas_evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    HAS_RAGAS = True
except ImportError as exc:  # pragma: no cover
    RAGAS_IMPORT_ERROR = str(exc)


def build_eval_rows(
    qa_pairs: list[dict[str, Any]],
    limit: int | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    subset = qa_pairs[:limit] if limit else qa_pairs
    for row in subset:
        question = row["question"]
        answer, contexts = mock_rag_pipeline(question, qa_pairs)
        rows.append(
            {
                "question": question,
                "answer": answer,
                "contexts": contexts,
                "ground_truth": row.get("ground_truth_answer", ""),
                "ground_truth_contexts": row.get("ground_truth_contexts", []),
            }
        )
    return rows


def evaluate_with_mock(rows: list[dict[str, Any]]) -> dict[str, Any]:
    per_sample: list[dict[str, Any]] = []
    sums = {"faithfulness": 0.0, "answer_relevance": 0.0, "context_precision": 0.0, "context_recall": 0.0}

    for row in rows:
        sample = RAGEvalInput(
            question=row["question"],
            answer=row["answer"],
            contexts=row["contexts"],
            ground_truth_answer=row.get("ground_truth", ""),
            ground_truth_contexts=row.get("ground_truth_contexts", []),
        )
        scores = evaluate_rag_sample(sample)
        per_sample.append({"question": row["question"], **scores.to_dict()})
        sums["faithfulness"] += scores.faithfulness
        sums["answer_relevance"] += scores.answer_relevance
        sums["context_precision"] += scores.context_precision
        sums["context_recall"] += scores.context_recall

    n = max(len(rows), 1)
    aggregate = {k: round(v / n, 4) for k, v in sums.items()}
    return {
        "engine": "mock_heuristic",
        "ragas_available": False,
        "import_error": RAGAS_IMPORT_ERROR,
        "sample_count": len(rows),
        "aggregate": aggregate,
        "samples": per_sample,
    }


def evaluate_with_ragas(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """调用 Ragas 官方评估（需 LLM / embedding 配置，课堂默认仍可能走 mock）。"""
    dataset_rows = {
        "question": [r["question"] for r in rows],
        "answer": [r["answer"] for r in rows],
        "contexts": [r["contexts"] for r in rows],
        "ground_truth": [r.get("ground_truth", "") for r in rows],
        "ground_truths": [r.get("ground_truth_contexts", []) for r in rows],
    }
    ds = Dataset.from_dict(dataset_rows)
    metrics = [faithfulness, answer_relevancy, context_precision, context_recall]

    try:
        result = ragas_evaluate(ds, metrics=metrics)
        df = result.to_pandas()
        aggregate = {col: round(float(df[col].mean()), 4) for col in df.columns if col in {
            "faithfulness", "answer_relevancy", "context_precision", "context_recall"
        }}
        return {
            "engine": "ragas",
            "ragas_available": True,
            "sample_count": len(rows),
            "aggregate": aggregate,
            "per_metric_columns": list(df.columns),
        }
    except Exception as exc:  # pragma: no cover - 无 Key 时常见
        fallback = evaluate_with_mock(rows)
        fallback["engine"] = "mock_fallback"
        fallback["ragas_error"] = str(exc)
        return fallback


def run_evaluation(
    qa_path: Path | None = None,
    limit: int | None = 5,
    force_mock: bool = False,
) -> dict[str, Any]:
    qa_pairs = load_qa_pairs(qa_path or DEFAULT_QA_PATH)
    rows = build_eval_rows(qa_pairs, limit=limit)

    if HAS_RAGAS and not force_mock:
        return evaluate_with_ragas(rows)
    return evaluate_with_mock(rows)


def print_report(report: dict[str, Any]) -> None:
    print("=" * 56)
    print("Day 34 · ragas_eval.py")
    print("=" * 56)
    print(f"评估引擎 : {report['engine']}")
    print(f"样本数量 : {report['sample_count']}")
    if not report.get("ragas_available", True):
        print(f"Ragas    : 未安装或强制 mock ({report.get('import_error', '')})")
    if report.get("ragas_error"):
        print(f"Ragas 回退原因: {report['ragas_error']}")

    print("\n聚合指标：")
    agg = report.get("aggregate", {})
    labels = {
        "faithfulness": "faithfulness（忠实度）",
        "answer_relevance": "answer_relevance（答案相关）",
        "answer_relevancy": "answer_relevancy（答案相关）",
        "context_precision": "context_precision（精确率）",
        "context_recall": "context_recall（召回率）",
    }
    for key, label in labels.items():
        if key in agg:
            print(f"  {label:32s}: {agg[key]:.4f}")

    if report.get("samples"):
        print("\n样本明细（前 2 条）：")
        for sample in report["samples"][:2]:
            print(f"  Q: {sample['question']}")
            print(
                f"     F={sample['faithfulness']:.3f} "
                f"R={sample['answer_relevance']:.3f} "
                f"CP={sample['context_precision']:.3f} "
                f"CR={sample['context_recall']:.3f}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Day 34 Ragas / mock RAG 评估")
    parser.add_argument("--qa-file", type=Path, default=DEFAULT_QA_PATH)
    parser.add_argument("--limit", type=int, default=5, help="评估样本上限")
    parser.add_argument("--force-mock", action="store_true", help="强制启发式 mock")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    report = run_evaluation(
        qa_path=args.qa_file,
        limit=args.limit,
        force_mock=args.force_mock,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
