# -*- coding: utf-8 -*-
"""
Day 34 · 构建 RAG 评估测试集

从知识库 Markdown 与种子 QA 合并生成 sample_qa_pairs.json，
供 rag_eval_demo.py / ragas_eval.py 使用。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

CODE_DIR = Path(__file__).resolve().parent
DATA_DIR = CODE_DIR / "data"
DEFAULT_OUTPUT = CODE_DIR / "sample_qa_pairs.json"
SEED_PATH = CODE_DIR / "sample_qa_pairs.json"

# 种子模板：当文件不存在或需要扩充时使用
SEED_QA: list[dict[str, Any]] = [
    {
        "id": "eval_001",
        "category": "退款",
        "question": "如何申请退款？",
        "ground_truth_answer": "在订单详情页点击「申请退款」，填写原因后提交，1-3 个工作日审核。",
        "ground_truth_contexts": [
            "退款流程：用户进入订单详情页，点击「申请退款」按钮，填写退款原因并提交申请。"
        ],
        "tags": ["faq", "refund"],
    },
]


@dataclass
class QAPair:
    id: str
    category: str
    question: str
    ground_truth_answer: str
    ground_truth_contexts: list[str]
    tags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def slugify(text: str) -> str:
    text = re.sub(r"\s+", "_", text.strip())
    return re.sub(r"[^\w\u4e00-\u9fff-]", "", text)[:24] or "item"


def parse_markdown_sections(path: Path) -> list[dict[str, str]]:
    """按 ## 标题切分 Markdown 段落。"""
    text = path.read_text(encoding="utf-8")
    sections: list[dict[str, str]] = []
    current_title = "概述"
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append({
                    "title": current_title,
                    "body": "\n".join(current_lines).strip(),
                    "source": path.name,
                })
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append({
            "title": current_title,
            "body": "\n".join(current_lines).strip(),
            "source": path.name,
        })
    return [s for s in sections if s["body"]]


def section_to_question(title: str) -> str:
    """由章节标题生成自然问句。"""
    mapping = {
        "退款流程": "如何申请退款？",
        "退款到账时间": "退款多久能到账？",
        "密码找回": "忘记密码怎么办？",
        "修改密码": "怎么修改登录密码？",
        "模型支持": "星火智服支持哪些大模型？",
        "数据安全": "知识库文档会上传到公网吗？",
        "人工客服": "如何联系人工客服？",
        "电子发票": "如何开具电子发票？",
        "发货时效": "现货订单什么时候发货？",
    }
    if title in mapping:
        return mapping[title]
    if "如何" in title or "怎么" in title:
        return title if title.endswith("？") else f"{title}？"
    return f"{title}是什么？"


def extract_answer(body: str, max_len: int = 120) -> str:
    """取首句或前 max_len 字作为标准答案。"""
    body = body.strip()
    for sep in ("。", "；", "\n"):
        if sep in body:
            first = body.split(sep)[0].strip()
            if first:
                return first + ("。" if sep == "。" else "")
    return body[:max_len] + ("..." if len(body) > max_len else "")


def load_seed_pairs(path: Path) -> list[dict[str, Any]]:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return list(SEED_QA)


def build_from_kb(data_dir: Path) -> list[QAPair]:
    pairs: list[QAPair] = []
    idx = 100
    for md_path in sorted(data_dir.glob("*.md")):
        category = md_path.stem.replace("kb_", "")
        for section in parse_markdown_sections(md_path):
            idx += 1
            question = section_to_question(section["title"])
            context = f"{section['title']}：{section['body']}"
            pairs.append(
                QAPair(
                    id=f"kb_{idx:03d}",
                    category=category,
                    question=question,
                    ground_truth_answer=extract_answer(section["body"]),
                    ground_truth_contexts=[context],
                    tags=["auto", category, section["source"]],
                )
            )
    return pairs


def merge_pairs(
    seed: list[dict[str, Any]],
    generated: list[QAPair],
    dedupe_by_question: bool = True,
) -> list[dict[str, Any]]:
    """合并种子与自动生成条目，按 question 去重（种子优先）。"""
    merged: dict[str, dict[str, Any]] = {}
    for row in seed:
        merged[row["question"]] = row
    if not dedupe_by_question:
        return list(merged.values()) + [p.to_dict() for p in generated]

    for pair in generated:
        if pair.question not in merged:
            merged[pair.question] = pair.to_dict()
    return list(merged.values())


def validate_pairs(pairs: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    required = ("id", "question", "ground_truth_answer", "ground_truth_contexts")
    for i, row in enumerate(pairs):
        for key in required:
            if key not in row or not row[key]:
                errors.append(f"第 {i} 条缺少字段: {key}")
        if row.get("ground_truth_contexts") and not isinstance(row["ground_truth_contexts"], list):
            errors.append(f"第 {i} 条 ground_truth_contexts 应为 list")
    return errors


def build_test_set(
    data_dir: Path | None = None,
    output_path: Path | None = None,
    seed_path: Path | None = None,
) -> list[dict[str, Any]]:
    data_dir = data_dir or DATA_DIR
    output_path = output_path or DEFAULT_OUTPUT
    seed_path = seed_path or SEED_PATH

    seed = load_seed_pairs(seed_path)
    generated = build_from_kb(data_dir) if data_dir.is_dir() else []
    pairs = merge_pairs(seed, generated)

    errors = validate_pairs(pairs)
    if errors:
        raise ValueError("测试集校验失败:\n" + "\n".join(errors))

    output_path.write_text(
        json.dumps(pairs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return pairs


def main() -> None:
    pairs = build_test_set()
    print("=" * 56)
    print("Day 34 · build_test_set.py")
    print("=" * 56)
    print(f"输出: {DEFAULT_OUTPUT}")
    print(f"条数: {len(pairs)}")
    print("\n前 3 条预览：")
    for row in pairs[:3]:
        print(f"  - [{row['id']}] {row['question']}")
    print("\n[OK] 测试集构建完成")


if __name__ == "__main__":
    main()
