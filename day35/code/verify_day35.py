# -*- coding: utf-8 -*-
"""
Day 35 验收脚本

运行：cd day35/code && python3 verify_day35.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

DATA_DIR = CODE_DIR / "data" / "kb_docs"
COMPARE_DOC = CODE_DIR / "compare_frameworks.md"


def run_script(name: str, extra: list[str] | None = None) -> bool:
    path = CODE_DIR / name
    cmd = [sys.executable, str(path)] + (extra or [])
    print(f"\n{'=' * 50}\n运行 {' '.join(cmd)}\n{'=' * 50}")
    result = subprocess.run(cmd, cwd=CODE_DIR)
    ok = result.returncode == 0
    print(f"[{'OK' if ok else 'FAIL'}] {name}")
    return ok


def check_imports() -> bool:
    try:
        from llamaindex_kb import create_kb_engine, MockKBEngine  # noqa: F401
    except ImportError as exc:
        print(f"[FAIL] import: {exc}")
        return False
    print("[OK] import llamaindex_kb")
    return True


def check_kb_docs() -> bool:
    if not DATA_DIR.is_dir():
        print(f"[FAIL] 知识库目录缺失: {DATA_DIR}")
        return False
    md_files = list(DATA_DIR.glob("**/*.md"))
    if len(md_files) < 3:
        print(f"[FAIL] kb_docs 文件过少: {len(md_files)}")
        return False
    print(f"[OK] kb_docs ({len(md_files)} 个文件)")
    return True


def check_compare_doc() -> bool:
    if not COMPARE_DOC.is_file():
        print("[FAIL] compare_frameworks.md 缺失")
        return False
    text = COMPARE_DOC.read_text(encoding="utf-8")
    for keyword in ("LangChain", "LlamaIndex", "RAG"):
        if keyword not in text:
            print(f"[FAIL] compare_frameworks.md 缺少关键词: {keyword}")
            return False
    print("[OK] compare_frameworks.md")
    return True


def check_mock_engine_load() -> bool:
    from llamaindex_kb import create_kb_engine

    engine = create_kb_engine(DATA_DIR, force_mock=True)
    count = engine.load()
    if count < 8:
        print(f"[FAIL] mock 索引单元过少: {count}")
        return False
    print(f"[OK] mock 引擎加载 {count} 个 chunk")
    return True


def check_refund_query() -> bool:
    from llamaindex_kb import create_kb_engine

    engine = create_kb_engine(DATA_DIR, force_mock=True)
    engine.load()
    result = engine.query("如何申请退款？")
    if "退款" not in result.answer and "退款" not in " ".join(c.text for c in result.chunks):
        print(f"[FAIL] 退款问答未命中: {result.answer}")
        return False
    if not result.chunks:
        print("[FAIL] 未返回检索片段")
        return False
    print(f"[OK] 退款问答 -> {result.answer[:60]}...")
    return True


def check_password_query() -> bool:
    from llamaindex_kb import create_kb_engine

    engine = create_kb_engine(DATA_DIR, force_mock=True)
    engine.load()
    result = engine.query("忘记密码怎么办？")
    blob = result.answer + " ".join(c.text for c in result.chunks)
    if "密码" not in blob:
        print(f"[FAIL] 密码问答未命中: {result.answer}")
        return False
    print("[OK] 密码问答命中")
    return True


def main() -> int:
    print("Day 35 verify_day35.py")
    results = [
        check_imports(),
        check_kb_docs(),
        check_compare_doc(),
        check_mock_engine_load(),
        check_refund_query(),
        check_password_query(),
        run_script("llamaindex_kb.py", ["--force-mock", "-q", "如何申请退款？"]),
    ]
    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 50}")
    print(f"验收结果: {passed}/{total} 通过")
    print("=" * 50)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
