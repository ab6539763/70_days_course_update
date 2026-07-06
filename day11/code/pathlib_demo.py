# -*- coding: utf-8 -*-
"""
Day 11 下午演示：os 与 pathlib 路径操作。
运行：cd day11/code && python3 pathlib_demo.py
"""

from __future__ import annotations

import os
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
DATA_DIR = CODE_DIR / "data"
DOCS_DIR = DATA_DIR / "sample_docs"
OUTPUT_DIR = CODE_DIR / "output"

TEXT_SUFFIXES = {".txt", ".md"}


def demo_path_basics() -> None:
    """Path 拼接、suffix、stem、parent。"""
    print("=" * 50)
    print("1. Path 基础属性")
    print("=" * 50)

    file_path = DOCS_DIR / "product_guide.md"
    print(f"完整路径: {file_path}")
    print(f"suffix:   {file_path.suffix}")
    print(f"stem:     {file_path.stem}")
    print(f"parent:   {file_path.parent}")
    print(f"exists:   {file_path.exists()}")
    print()


def demo_os_makedirs() -> None:
    """os.makedirs 与 Path.mkdir 对照。"""
    print("=" * 50)
    print("2. 创建输出目录")
    print("=" * 50)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nested = OUTPUT_DIR / "reports" / "2026"
    nested.mkdir(parents=True, exist_ok=True)
    print(f"os.makedirs: {OUTPUT_DIR}")
    print(f"Path.mkdir:  {nested}")
    print()


def demo_os_getenv() -> None:
    """读取环境变量（与 Day 10 get_env 呼应）。"""
    print("=" * 50)
    print("3. os.getenv 环境变量")
    print("=" * 50)

    user = os.getenv("USER", os.getenv("USERNAME", "unknown"))
    home = os.getenv("HOME", os.getenv("USERPROFILE", ""))
    print(f"当前用户: {user}")
    print(f"HOME:     {home or '(未设置)'}")
    print()


def iter_text_files(root: Path) -> list[Path]:
    """递归收集 txt/md 文件（与主工具相同逻辑）。"""
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return files


def demo_iterdir_vs_rglob() -> None:
    """iterdir 与 rglob 对比。"""
    print("=" * 50)
    print("4. 目录遍历 iterdir / rglob")
    print("=" * 50)

    print(f"扫描目录: {DOCS_DIR}")
    print("当前层 iterdir:")
    for item in sorted(DOCS_DIR.iterdir()):
        kind = "目录" if item.is_dir() else "文件"
        print(f"  [{kind}] {item.name}")

    print()
    print("递归 rglob 文本文件:")
    for path in iter_text_files(DOCS_DIR):
        rel = path.relative_to(DOCS_DIR)
        size = path.stat().st_size
        print(f"  {rel} ({size} bytes)")
    print()


def demo_resolve_relative() -> None:
    """绝对路径 resolve 与 relative_to。"""
    print("=" * 50)
    print("5. resolve 与 relative_to")
    print("=" * 50)

    sample = DOCS_DIR / "llm_intro.md"
    abs_path = sample.resolve()
    rel_path = sample.relative_to(DOCS_DIR)
    print(f"绝对路径: {abs_path}")
    print(f"相对 docs_dir: {rel_path}")
    print()


def main() -> None:
    print("Day 11 · pathlib_demo.py")
    print()
    demo_path_basics()
    demo_os_makedirs()
    demo_os_getenv()
    demo_iterdir_vs_rglob()
    demo_resolve_relative()
    print("全部演示完成 ✓")


if __name__ == "__main__":
    main()
