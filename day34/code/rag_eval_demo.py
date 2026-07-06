# -*- coding: utf-8 -*-
"""
Day 34 · RAG 评估指标演示（教学版启发式实现）

指标：
- faithfulness（忠实度）：答案是否被检索上下文支撑
- answer_relevance（答案相关性）：答案是否回应问题
- context_precision（上下文精确率）：检索结果中相关片段占比
- context_recall（上下文召回率）：标准相关片段被检索到的比例

无 Ragas / 无 LLM Key 时可独立运行，用于理解指标含义。
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CODE_DIR = Path(__file__).resolve().parent
DEFAULT_QA_PATH = CODE_DIR / "sample_qa_pairs.json"

# 中文停用词（极简教学集）
STOPWORDS = {
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
    "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
    "自己", "这", "那", "吗", "呢", "吧", "啊", "什么", "如何", "怎么", "哪些",
}


def tokenize(text: str) -> set[str]:
    """粗粒度中文分词：连续汉字/字母/数字片段 + 中文二元组。"""
    text = text.lower().strip()
    tokens = set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-z0-9]{2,}", text))
    han = re.sub(r"[^\u4e00-\u9fff]", "", text)
    for i in range(len(han) - 1):
        grams = han[i : i + 2]
        if grams not in STOPWORDS:
            tokens.add(grams)
    return {t for t in tokens if t not in STOPWORDS and len(t) > 1}


def jaccard_similarity(a: str, b: str) -> float:
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def split_sentences(text: str) -> list[str]:
  parts = re.split(r"[。！？；\n]+", text)
  return [p.strip() for p in parts if p.strip()]


@dataclass
class RAGEvalInput:
    question: str
    answer: str
    contexts: list[str]
    ground_truth_answer: str = ""
    ground_truth_contexts: list[str] = field(default_factory=list)


@dataclass
class RAGEvalScores:
    faithfulness: float
    answer_relevance: float
    context_precision: float
    context_recall: float
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "faithfulness": round(self.faithfulness, 4),
            "answer_relevance": round(self.answer_relevance, 4),
            "context_precision": round(self.context_precision, 4),
            "context_recall": round(self.context_recall, 4),
            "details": self.details,
        }

    @property
    def average(self) -> float:
        return (
            self.faithfulness
            + self.answer_relevance
            + self.context_precision
            + self.context_recall
        ) / 4.0


def score_faithfulness(answer: str, contexts: list[str]) -> tuple[float, dict[str, Any]]:
    """
    忠实度：答案每个句子在上下文中的最大支撑度均值。

    教学近似：句子与任一 context 的 Jaccard 相似度 > 0.15 视为有支撑。
    """
    if not answer.strip():
        return 0.0, {"supported_sentences": 0, "total_sentences": 0}

    ctx_blob = "\n".join(contexts)
    sentences = split_sentences(answer)
    if not sentences:
        sentences = [answer.strip()]

    supported = 0
    scores: list[float] = []
    for sent in sentences:
        sim = max(jaccard_similarity(sent, ctx_blob), *(jaccard_similarity(sent, c) for c in contexts))
        scores.append(sim)
        if sim >= 0.15:
            supported += 1

    ratio = supported / len(sentences)
    avg_sim = sum(scores) / len(scores)
    # 综合：支撑比例 70% + 平均相似度 30%
    score = 0.7 * ratio + 0.3 * avg_sim
    return min(1.0, score), {
        "supported_sentences": supported,
        "total_sentences": len(sentences),
        "sentence_scores": [round(s, 4) for s in scores],
    }


def score_answer_relevance(question: str, answer: str) -> tuple[float, dict[str, Any]]:
    """答案相关性：问题与答案的语义重叠（教学用 Jaccard）。"""
    sim = jaccard_similarity(question, answer)
    # 过短答案惩罚
    penalty = 1.0 if len(answer.strip()) >= 8 else 0.5
    return min(1.0, sim * 1.2 * penalty), {"jaccard": round(sim, 4)}


def _context_is_relevant(ctx: str, question: str, gt_contexts: list[str]) -> bool:
    if jaccard_similarity(ctx, question) >= 0.12:
        return True
    for gt in gt_contexts:
        if jaccard_similarity(ctx, gt) >= 0.25:
            return True
    return False


def score_context_precision(
    question: str,
    contexts: list[str],
    ground_truth_contexts: list[str],
) -> tuple[float, dict[str, Any]]:
    """上下文精确率：检索到的 context 中相关条目的比例。"""
    if not contexts:
        return 0.0, {"relevant": 0, "retrieved": 0}

    flags = [
        _context_is_relevant(ctx, question, ground_truth_contexts) for ctx in contexts
    ]
    relevant = sum(1 for f in flags if f)
    precision = relevant / len(contexts)
    return precision, {
        "relevant": relevant,
        "retrieved": len(contexts),
        "per_context_relevant": flags,
    }


def score_context_recall(
    contexts: list[str],
    ground_truth_contexts: list[str],
) -> tuple[float, dict[str, Any]]:
    """上下文召回率：标准相关片段被检索覆盖的比例。"""
    if not ground_truth_contexts:
        return 1.0, {"matched_gt": 0, "total_gt": 0}

    retrieved_blob = "\n".join(contexts)
    matched = 0
    per_gt: list[float] = []
    for gt in ground_truth_contexts:
        sim_ctx = max(
            jaccard_similarity(gt, retrieved_blob),
            *(jaccard_similarity(gt, c) for c in contexts),
        )
        per_gt.append(sim_ctx)
        if sim_ctx >= 0.25:
            matched += 1

    recall = matched / len(ground_truth_contexts)
    return recall, {
        "matched_gt": matched,
        "total_gt": len(ground_truth_contexts),
        "gt_similarities": [round(s, 4) for s in per_gt],
    }


def evaluate_rag_sample(sample: RAGEvalInput) -> RAGEvalScores:
    f_score, f_detail = score_faithfulness(sample.answer, sample.contexts)
    r_score, r_detail = score_answer_relevance(sample.question, sample.answer)
    cp_score, cp_detail = score_context_precision(
        sample.question, sample.contexts, sample.ground_truth_contexts
    )
    cr_score, cr_detail = score_context_recall(sample.contexts, sample.ground_truth_contexts)

    return RAGEvalScores(
        faithfulness=f_score,
        answer_relevance=r_score,
        context_precision=cp_score,
        context_recall=cr_score,
        details={
            "faithfulness": f_detail,
            "answer_relevance": r_detail,
            "context_precision": cp_detail,
            "context_recall": cr_detail,
        },
    )


def load_qa_pairs(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or DEFAULT_QA_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def mock_rag_pipeline(question: str, qa_pairs: list[dict[str, Any]]) -> tuple[str, list[str]]:
    """
    模拟 RAG：按问题与 QA 条目的重叠选 context，并返回 ground_truth_answer 作答案。
    故意混入一条噪声 context 以演示 context_precision。
    """
    ranked = sorted(
        qa_pairs,
        key=lambda row: jaccard_similarity(question, row["question"]),
        reverse=True,
    )
    best = ranked[0] if ranked else None
    if not best:
        return "暂无相关信息。", []

    contexts = list(best.get("ground_truth_contexts", []))
    # 噪声片段：降低 precision 的教学演示
    noise = "今日天气晴朗，适合户外活动。本段与客服知识库无关，用于测试检索噪声。"
    contexts.append(noise)
    answer = best.get("ground_truth_answer", "")
    return answer, contexts


def format_report(question: str, scores: RAGEvalScores) -> str:
    lines = [
        f"问题：{question}",
        "-" * 48,
        f"faithfulness（忠实度）      : {scores.faithfulness:.4f}",
        f"answer_relevance（答案相关）: {scores.answer_relevance:.4f}",
        f"context_precision（精确率）: {scores.context_precision:.4f}",
        f"context_recall（召回率）    : {scores.context_recall:.4f}",
        f"综合均值                    : {scores.average:.4f}",
    ]
    return "\n".join(lines)


def demo() -> None:
    qa_pairs = load_qa_pairs()
    question = "如何申请退款？"
    answer, contexts = mock_rag_pipeline(question, qa_pairs)
    gt = next((row for row in qa_pairs if row["question"] == question), qa_pairs[0])

    sample = RAGEvalInput(
        question=question,
        answer=answer,
        contexts=contexts,
        ground_truth_answer=gt.get("ground_truth_answer", ""),
        ground_truth_contexts=gt.get("ground_truth_contexts", []),
    )
    scores = evaluate_rag_sample(sample)

    print("=" * 56)
    print("Day 34 · rag_eval_demo.py")
    print("=" * 56)
    print(format_report(question, scores))
    print("\n检索上下文：")
    for i, ctx in enumerate(contexts, 1):
        print(f"  [{i}] {ctx[:60]}{'...' if len(ctx) > 60 else ''}")
    print("\n指标说明：")
    print("  · faithfulness：答案是否『有据可查』，防幻觉")
    print("  · answer_relevance：答非所问会扣分")
    print("  · context_precision：检索噪声越多分越低")
    print("  · context_recall：该召回的片段是否都召回了")


if __name__ == "__main__":
    demo()
