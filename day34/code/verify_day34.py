# -*- coding: utf-8 -*-
"""
Day 34 验收脚本

运行：cd day34/code && python3 verify_day34.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

SCRIPTS = [
    "build_test_set.py",
    "rag_eval_demo.py",
    "ragas_eval.py",
]


def run_script(name: str, extra_args: list[str] | None = None) -> bool:
    path = CODE_DIR / name
    cmd = [sys.executable, str(path)] + (extra_args or [])
    print(f"\n{'=' * 50}\n运行 {' '.join(cmd)}\n{'=' * 50}")
    result = subprocess.run(cmd, cwd=CODE_DIR)
    ok = result.returncode == 0
    print(f"[{'OK' if ok else 'FAIL'}] {name}")
    return ok


def check_imports() -> bool:
    try:
        from rag_eval_demo import evaluate_rag_sample, RAGEvalInput  # noqa: F401
        from build_test_set import build_test_set  # noqa: F401
        from ragas_eval import run_evaluation  # noqa: F401
    except ImportError as exc:
        print(f"[FAIL] import: {exc}")
        return False
    print("[OK] import 全部模块")
    return True


def check_sample_data() -> bool:
    path = CODE_DIR / "sample_qa_pairs.json"
    if not path.is_file():
        print("[FAIL] sample_qa_pairs.json 缺失")
        return False
    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data) < 5:
        print(f"[FAIL] QA 条数过少: {len(data)}")
        return False
    required = ("question", "ground_truth_answer", "ground_truth_contexts")
    for row in data:
        if any(k not in row for k in required):
            print(f"[FAIL] 字段不完整: {row.get('id')}")
            return False
    print(f"[OK] sample_qa_pairs.json ({len(data)} 条)")
    return True


def check_metrics() -> bool:
    from rag_eval_demo import RAGEvalInput, evaluate_rag_sample

    sample = RAGEvalInput(
        question="如何申请退款？",
        answer="在订单详情页点击申请退款，1-3 个工作日审核。",
        contexts=["退款流程：用户进入订单详情页，点击申请退款按钮提交。"],
        ground_truth_contexts=["退款流程：用户进入订单详情页，点击「申请退款」按钮。"],
    )
    scores = evaluate_rag_sample(sample)
    if scores.faithfulness < 0.01:
        print(f"[FAIL] faithfulness 过低: {scores.faithfulness}")
        return False
    if scores.answer_relevance <= 0:
        print("[FAIL] answer_relevance 应 > 0")
        return False
    if not (0 <= scores.context_precision <= 1):
        print("[FAIL] context_precision 越界")
        return False
    if not (0 <= scores.context_recall <= 1):
        print("[FAIL] context_recall 越界")
        return False
    print(
        f"[OK] 指标计算 F={scores.faithfulness:.3f} "
        f"R={scores.answer_relevance:.3f} CP={scores.context_precision:.3f} "
        f"CR={scores.context_recall:.3f}"
    )
    return True


def check_build_test_set() -> bool:
    from build_test_set import build_test_set

    out = CODE_DIR / "_verify_qa.json"
    try:
        pairs = build_test_set(output_path=out)
        if len(pairs) < 5:
            print(f"[FAIL] build_test_set 条数不足: {len(pairs)}")
            return False
        print(f"[OK] build_test_set 生成 {len(pairs)} 条")
        return True
    finally:
        if out.exists():
            out.unlink()


def check_ragas_mock() -> bool:
    from ragas_eval import run_evaluation

    report = run_evaluation(limit=3, force_mock=True)
    agg = report.get("aggregate", {})
    if report.get("engine") not in ("mock_heuristic", "mock_fallback"):
        print(f"[FAIL] 强制 mock 引擎异常: {report.get('engine')}")
        return False
    for key in ("faithfulness", "context_precision", "context_recall"):
        if key not in agg:
            print(f"[FAIL] 缺少聚合指标 {key}")
            return False
    print(f"[OK] ragas_eval mock 引擎 aggregate={agg}")
    return True


def main() -> int:
    print("Day 34 verify_day34.py")
    results = [
        check_imports(),
        check_sample_data(),
        check_metrics(),
        check_build_test_set(),
        check_ragas_mock(),
        *[run_script(s, ["--force-mock"] if s == "ragas_eval.py" else None) for s in SCRIPTS],
    ]
    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 50}")
    print(f"验收结果: {passed}/{total} 通过")
    print("=" * 50)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
