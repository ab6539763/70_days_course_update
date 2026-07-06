# -*- coding: utf-8 -*-
"""
Day 11 下午演示：datetime、random、re 正则入门。
运行：cd day11/code && python3 regex_demo.py
"""

from __future__ import annotations

import random
import re
from datetime import datetime
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
DOCS_DIR = CODE_DIR / "data" / "sample_docs"


def demo_datetime() -> None:
    """时间戳用于报告文件名与 JSON 字段。"""
    print("=" * 50)
    print("1. datetime 时间戳")
    print("=" * 50)

    now = datetime.now()
    print(f"now:              {now}")
    print(f"strftime 文件名:    keyword_report_{now.strftime('%Y%m%d_%H%M%S')}.json")
    print(f"isoformat 报告:   {now.isoformat(timespec='seconds')}")
    print()


def demo_random() -> None:
    """随机抽样用于审计演示。"""
    print("=" * 50)
    print("2. random 抽样")
    print("=" * 50)

    keywords = ["退款", "大模型", "工单", "星火智服", "客服"]
    print(f"随机关键词: {random.choice(keywords)}")
    print(f"模拟重试间隔: {random.randint(1, 5)} 秒")

    files = list(DOCS_DIR.glob("*.md")) + list(DOCS_DIR.glob("*.txt"))
    if files:
        picked = random.choice(files)
        print(f"随机抽 1 份文档做人工核对: {picked.name}")
    print()


def demo_re_search_findall() -> None:
    """re.search / findall 基础。"""
    print("=" * 50)
    print("3. re.search 与 re.findall")
    print("=" * 50)

    text = "星火智服支持大模型问答，大模型可转工单。RAG 与大模型结合。"
    keyword = "大模型"
    pattern = re.escape(keyword)

    first = re.search(pattern, text)
    all_hits = re.findall(pattern, text)
    print(f"文本: {text}")
    print(f"search 首次位置: {first.start() if first else None}")
    print(f"findall 命中次数: {len(all_hits)} → {all_hits}")
    print()


def demo_re_ignorecase() -> None:
    """忽略大小写匹配英文。"""
    print("=" * 50)
    print("4. re.IGNORECASE")
    print("=" * 50)

    text = "RAG loader and rag pipeline for SparkTech."
    hits = re.findall(r"rag", text, re.IGNORECASE)
    print(f"忽略大小写 'rag' 命中: {len(hits)} 次")
    print()


def demo_re_sub_mask() -> None:
    """re.sub 手机号脱敏预习。"""
    print("=" * 50)
    print("5. re.sub 脱敏")
    print("=" * 50)

    text = "请联系客服 13800138001 或 13900139002 查询工单。"
    masked = re.sub(
        r"(?<!\d)(1\d{10})(?!\d)",
        lambda m: f"{m.group(1)[:3]}****{m.group(1)[-4:]}",
        text,
    )
    print(f"原文: {text}")
    print(f"脱敏: {masked}")
    print()


def demo_keyword_count_on_real_doc() -> None:
    """对真实样例文档统计关键词。"""
    print("=" * 50)
    print("6. 样例文档关键词统计")
    print("=" * 50)

    path = DOCS_DIR / "faq_refund.txt"
    text = path.read_text(encoding="utf-8")
    keywords = ["退款", "大模型", "工单"]
    for kw in keywords:
        count = len(re.findall(re.escape(kw), text))
        print(f"  {kw}: {count}")
    print()


def main() -> None:
    print("Day 11 · regex_demo.py")
    print()
    demo_datetime()
    demo_random()
    demo_re_search_findall()
    demo_re_ignorecase()
    demo_re_sub_mask()
    demo_keyword_count_on_real_doc()
    print("全部演示完成 ✓")


if __name__ == "__main__":
    main()
