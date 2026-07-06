# -*- coding: utf-8 -*-
"""
Day 20 验收脚本

运行：cd day20/code && python3 verify_day20.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np

CODE_DIR = Path(__file__).resolve().parent

SCRIPTS = [
    "cosine_similarity.py",
    "embedding_demo.py",
    "multimodal_demo.py",
    "similar_question_matcher.py",
]


def run_script(name: str) -> bool:
    path = CODE_DIR / name
    print(f"\n{'=' * 50}\n运行 {name}\n{'=' * 50}")
    result = subprocess.run([sys.executable, str(path)], cwd=CODE_DIR)
    ok = result.returncode == 0
    print(f"[{'OK' if ok else 'FAIL'}] {name}")
    return ok


def check_imports() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    try:
        from cosine_similarity import cosine_similarity  # noqa: F401
        from embedding_demo import EmbeddingClient, mock_embed_text  # noqa: F401
        from multimodal_demo import MultimodalClient  # noqa: F401
        from similar_question_matcher import SimilarQuestionMatcher  # noqa: F401
    except ImportError as exc:
        print(f"[FAIL] import: {exc}")
        return False
    print("[OK] import 全部模块")
    return True


def check_cosine() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    from cosine_similarity import cosine_similarity

    a = np.array([1.0, 0.0])
    b = np.array([1.0, 0.0])
    if abs(cosine_similarity(a, b) - 1.0) > 1e-9:
        print("[FAIL] 相同向量余弦应约为 1.0")
        return False
    print("[OK] cosine_similarity 基础运算")
    return True


def check_mock_embedding() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    from embedding_demo import mock_embed_text

    v1 = mock_embed_text("测试")
    v2 = mock_embed_text("测试")
    v3 = mock_embed_text("另一段文本")
    if v1 != v2:
        print("[FAIL] 相同文本 mock 向量应一致")
        return False
    if v1 == v3:
        print("[FAIL] 不同文本 mock 向量应不同")
        return False
    print("[OK] mock embedding 确定性")
    return True


def check_matcher() -> bool:
    sys.path.insert(0, str(CODE_DIR))
    from similar_question_matcher import SimilarQuestionMatcher

    matcher = SimilarQuestionMatcher(threshold=0.5)
    matcher.load()
    result = matcher.match("如何申请退款")
    if not result.matched:
        print(f"[FAIL] 应匹配退款 FAQ: {result.to_dict()}")
        return False
    if "退款" not in result.matched.question:
        print(f"[FAIL] 匹配问句异常: {result.matched.question}")
        return False
    print(f"[OK] matcher -> {result.matched.question} (score={result.score:.4f})")
    return True


def check_sample_data() -> bool:
    path = CODE_DIR / "sample_questions.json"
    if not path.is_file():
        print("[FAIL] sample_questions.json 缺失")
        return False
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data) < 5:
        print(f"[FAIL] FAQ 条数过少: {len(data)}")
        return False
    print(f"[OK] sample_questions.json ({len(data)} 条)")
    return True


def main() -> int:
    print("Day 20 verify_day20.py")
    results = [
        check_imports(),
        check_cosine(),
        check_mock_embedding(),
        check_sample_data(),
        check_matcher(),
        *[run_script(s) for s in SCRIPTS],
    ]
    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 50}")
    print(f"验收结果: {passed}/{total} 通过")
    print("=" * 50)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
