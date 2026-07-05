# -*- coding: utf-8 -*-
"""
Day 11 上午演示：txt / csv / json 文件读写。
运行：cd day11/code && python3 file_io_demo.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
DATA_DIR = CODE_DIR / "data"
OUTPUT_DIR = CODE_DIR / "output"


def demo_txt_read_write() -> None:
    """演示 with open 读写 UTF-8 文本。"""
    print("=" * 50)
    print("1. TXT 读写（with + encoding=utf-8）")
    print("=" * 50)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "demo_notes.txt"

    lines = [
        "星火智服 · 文件 IO 演示",
        "中文内容应原样保存，不乱码。",
        "第二行：退款、大模型、工单",
    ]
    with open(out_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    with open(out_path, encoding="utf-8") as f:
        content = f.read()

    print(f"写入路径: {out_path}")
    print("读回内容:")
    print(content)
    print()


def demo_csv_read_write() -> None:
    """演示 csv 模块读写 DictReader / DictWriter。"""
    print("=" * 50)
    print("2. CSV 读写（newline='' + utf-8）")
    print("=" * 50)

    src = DATA_DIR / "sample_contacts.csv"
    out_path = OUTPUT_DIR / "demo_contacts_copy.csv"

    rows: list[dict[str, str]] = []
    with open(src, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))

    print(f"从 {src.name} 读取 {len(rows)} 行:")
    for row in rows:
        print(f"  {row['name']} | {row['phone']} | {row['department']}")

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "phone", "department"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"已复制到: {out_path}")
    print()


def demo_json_read_write() -> None:
    """演示 json.load / json.dump，中文 ensure_ascii=False。"""
    print("=" * 50)
    print("3. JSON 读写（ensure_ascii=False）")
    print("=" * 50)

    src = DATA_DIR / "sample_config.json"
    out_path = OUTPUT_DIR / "demo_config_copy.json"

    with open(src, encoding="utf-8") as f:
        config = json.load(f)

    print(f"项目: {config['project']}")
    print(f"默认关键词: {config['default_keywords']}")

    config["demo_note"] = "由 file_io_demo.py 写入"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"已写入: {out_path}")
    print()


def demo_pathlib_read_text() -> None:
    """演示 Path.read_text 快捷读法（小文件适用）。"""
    print("=" * 50)
    print("4. pathlib Path.read_text 读样例文档")
    print("=" * 50)

    sample = DATA_DIR / "sample_docs" / "faq_refund.txt"
    text = sample.read_text(encoding="utf-8")
    preview = text[:80].replace("\n", " ")
    print(f"文件: {sample.name}")
    print(f"字符数: {len(text)}")
    print(f"预览: {preview}...")
    print()


def main() -> None:
    print("Day 11 · file_io_demo.py")
    print()
    demo_txt_read_write()
    demo_csv_read_write()
    demo_json_read_write()
    demo_pathlib_read_text()
    print("全部演示完成 ✓")


if __name__ == "__main__":
    main()
