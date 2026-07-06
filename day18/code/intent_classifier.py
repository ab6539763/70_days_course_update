# -*- coding: utf-8 -*-
"""
Day 18 · 智能客服意图分类器（结构化 JSON 输出）

实操项目：对用户消息进行意图识别，输出标准 JSON，供下游路由与工单系统消费。

运行：cd day18/code && python3 intent_classifier.py
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from llm_client import INTENT_LABELS, LLMClient


SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": list(INTENT_LABELS)},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "slots": {"type": "object"},
        "need_human": {"type": "boolean"},
        "suggested_reply": {"type": "string"},
    },
    "required": ["intent", "confidence", "need_human", "suggested_reply"],
}


@dataclass
class IntentResult:
    intent: str
    confidence: float
    slots: dict[str, str] = field(default_factory=dict)
    need_human: bool = False
    suggested_reply: str = ""
    raw_text: str = ""
    mode: str = "mock"

    @classmethod
    def from_json(cls, text: str, mode: str = "mock") -> "IntentResult":
        data = json.loads(text)
        return cls(
            intent=data.get("intent", "其他"),
            confidence=float(data.get("confidence", 0.0)),
            slots=data.get("slots") or {},
            need_human=bool(data.get("need_human", False)),
            suggested_reply=data.get("suggested_reply", ""),
            raw_text=text,
            mode=mode,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "slots": self.slots,
            "need_human": self.need_human,
            "suggested_reply": self.suggested_reply,
            "mode": self.mode,
        }


def build_classifier_messages(user_message: str) -> list[dict[str, str]]:
    schema_hint = json.dumps(
        {
            "intent": "产品咨询",
            "confidence": 0.9,
            "slots": {},
            "need_human": False,
            "suggested_reply": "...",
        },
        ensure_ascii=False,
    )
    system = (
        "你是星火智服智能客服意图分类器。"
        f"合法 intent 取值：{', '.join(INTENT_LABELS)}。"
        "只输出 JSON，不要 markdown 代码块。"
    )
    user = f"""对用户消息进行意图分类。

<user_message>
{user_message}
</user_message>

输出 JSON schema 示例：
{schema_hint}
"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def extract_json_block(text: str) -> str:
    """从模型输出中提取 JSON（兼容 markdown 代码块）。"""
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fence:
        return fence.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


class IntentClassifier:
    def __init__(self, client: LLMClient | None = None) -> None:
        self._client = client or LLMClient()

    @property
    def mode(self) -> str:
        return self._client.mode

    def classify(self, user_message: str) -> IntentResult:
        messages = build_classifier_messages(user_message)
        response = self._client.chat(
            messages,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        payload = extract_json_block(response.text)
        return IntentResult.from_json(payload, mode=response.mode)


def load_sample_queries(path: Path | None = None) -> list[str]:
    p = path or Path(__file__).resolve().parent / "data" / "sample_queries.txt"
    if not p.is_file():
        return [
            "你好，在吗？",
            "你们的 API 怎么申请？",
            "订单 ORD-8821 到哪了？",
            "我要退款，商品有质量问题。",
            "登录一直提示密码错误。",
        ]
    lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()]
    return [ln for ln in lines if ln and not ln.startswith("#")]


def route_by_intent(result: IntentResult) -> str:
    """根据意图路由到下游队列（教学用）。"""
    routing = {
        "产品咨询": "bot_faq",
        "订单物流": "bot_order",
        "投诉退款": "human_complaint",
        "账户问题": "human_account",
        "技术支持": "bot_tech",
        "感谢寒暄": "bot_chitchat",
        "其他": "bot_fallback",
    }
    queue = routing.get(result.intent, "bot_fallback")
    if result.need_human:
        queue = f"human_escalation/{queue}"
    return queue


def run_batch_demo() -> list[dict[str, Any]]:
    classifier = IntentClassifier()
    rows: list[dict[str, Any]] = []
    for query in load_sample_queries():
        result = classifier.classify(query)
        rows.append(
            {
                "query": query,
                "result": result.to_dict(),
                "route": route_by_intent(result),
            }
        )
    return rows


def main() -> None:
    print("=" * 60)
    print("Day 18 · intent_classifier.py · 智能客服意图分类")
    print("=" * 60)

    classifier = IntentClassifier()
    print(f"LLM 模式: {classifier.mode}\n")

    for row in run_batch_demo():
        print(f"Q: {row['query']}")
        print(json.dumps(row["result"], ensure_ascii=False, indent=2))
        print(f"路由 → {row['route']}")
        print("-" * 40)

    print("\n✅ intent_classifier.py 完成")


if __name__ == "__main__":
    main()
