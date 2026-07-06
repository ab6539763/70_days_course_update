# -*- coding: utf-8 -*-
"""Day 28 验收脚本：Document Loader + Text Splitter。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=CODE_DIR, check=True)


def main() -> None:
    print("Day 28 verify_day28.py")
    ok = 0
    total = 5

    sample_dir = CODE_DIR / "data" / "sample_docs"
    if sample_dir.is_dir() and any(sample_dir.iterdir()):
        print("[OK] sample_docs 存在")
        ok += 1
    else:
        print("[FAIL] sample_docs 缺失")

    for script in ("doc_loader_demo.py", "text_splitter_demo.py", "process_pdf_ebook.py"):
        path = CODE_DIR / script
        if path.is_file():
            print(f"[OK] {script} 存在")
            ok += 1
        else:
            print(f"[FAIL] {script} 缺失")

    try:
        run([sys.executable, "ensure_samples.py"])
        run([sys.executable, "doc_loader_demo.py"])
        print("[OK] doc_loader_demo 可执行")
        ok += 1
    except subprocess.CalledProcessError as exc:
        print(f"[FAIL] doc_loader_demo: {exc}")

    print(f"\n验收结果: {ok}/{total}")
    if ok < total:
        sys.exit(1)
    print("全部通过 ✅")


if __name__ == "__main__":
    main()
