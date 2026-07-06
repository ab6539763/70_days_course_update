# -*- coding: utf-8 -*-
"""
Day 39 · 星火智服 Phase3 工单路由基础工具（无框架）

供手写 ReAct Agent 调用的确定性 mock 工具：
- classify_ticket：工单意图分类
- route_ticket：路由到技能组
- search_kb_snippet：知识库片段检索（对接 Day 36 RAG 概念）
- calc_priority_score：优先级评分计算
"""

from __future__ import annotations

import ast
import json
import operator
import re
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"
TICKETS_FILE = DATA_DIR / "mock_tickets.json"
KB_FILE = DATA_DIR / "mock_kb_snippets.json"

# 意图 → 技能组映射
INTENT_ROUTING: dict[str, dict[str, str]] = {
    "refund": {"team": "billing", "sla_hours": "24", "label": "退款/账单组"},
    "technical": {"team": "engineering", "sla_hours": "8", "label": "技术支持组"},
    "account": {"team": "customer_success", "sla_hours": "12", "label": "客户成功组"},
    "complaint": {"team": "escalation", "sla_hours": "4", "label": "投诉升级组"},
    "general": {"team": "l1_support", "sla_hours": "48", "label": "一线客服组"},
}

INTENT_KEYWORDS: dict[str, list[str]] = {
    "refund": ["退款", "退费", "账单", "发票", "扣款", "refund"],
    "technical": ["报错", "bug", "无法登录", "接口", "api", "崩溃", "technical"],
    "account": ["账号", "密码", "权限", "开通", "account"],
    "complaint": ["投诉", "差评", "态度", "投诉你们", "complaint"],
}

_SAFE_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class ToolError(ValueError):
    """工具业务错误。"""


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Num):  # noqa: SIM114
        return float(node.n)  # type: ignore[attr-defined]
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        if isinstance(node.op, (ast.Div, ast.FloorDiv)) and right == 0:
            raise ToolError("除数不能为零")
        return _SAFE_OPS[type(node.op)](left, right)
    raise ToolError(f"不支持的表达式: {type(node).__name__}")


def classify_ticket(text: str) -> dict[str, Any]:
    """根据工单描述做规则分类（mock 分类器）。"""
    text = text.strip()
    if not text:
        raise ToolError("text 不能为空")

    lowered = text.lower()
    scores: dict[str, int] = {intent: 0 for intent in INTENT_KEYWORDS}
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in lowered:
                scores[intent] += 1

    best_intent = max(scores, key=scores.get)  # type: ignore[arg-type]
    if scores[best_intent] == 0:
        best_intent = "general"

    confidence = min(0.95, 0.55 + scores.get(best_intent, 0) * 0.15)
    return {
        "intent": best_intent,
        "confidence": round(confidence, 2),
        "matched_keywords": [k for k in INTENT_KEYWORDS.get(best_intent, []) if k.lower() in lowered],
        "source": "mock_rule_classifier",
    }


def route_ticket(intent: str, customer_tier: str = "standard") -> dict[str, Any]:
    """将分类结果路由到技能组。"""
    intent = intent.strip().lower()
    if intent not in INTENT_ROUTING:
        intent = "general"

    route = INTENT_ROUTING[intent]
    tier_boost = {"vip": -2, "enterprise": -4, "standard": 0}.get(customer_tier.lower(), 0)
    sla = max(1, int(route["sla_hours"]) + tier_boost)

    return {
        "intent": intent,
        "team": route["team"],
        "team_label": route["label"],
        "sla_hours": sla,
        "customer_tier": customer_tier,
        "auto_routed": True,
        "source": "mock_router",
    }


def search_kb_snippet(query: str, limit: int = 3) -> dict[str, Any]:
    """
    检索知识库片段（mock，概念对齐 Day 36 project2 RAG）。

    生产环境应调用 day36/code/project2 的 hybrid retriever。
    """
    query = query.strip()
    if not query:
        raise ToolError("query 不能为空")

    limit = max(1, min(int(limit), 5))
    snippets = _load_json(KB_FILE)
    q = query.lower()
    matched: list[dict[str, Any]] = []

    for item in snippets:
        haystack = f"{item['title']} {item['content']}".lower()
        if q in haystack or any(tok in haystack for tok in q.split() if len(tok) > 1):
            matched.append(item)
        if len(matched) >= limit:
            break

    return {
        "query": query,
        "count": len(matched),
        "snippets": matched,
        "rag_ref": "../day36/code/project2/backend/rag_service.py",
        "source": "mock_kb_index",
    }


def calc_priority_score(urgency: int, impact: int, vip_bonus: int = 0) -> dict[str, Any]:
    """计算工单优先级分数：urgency * impact + vip_bonus。"""
    urgency = int(urgency)
    impact = int(impact)
    vip_bonus = int(vip_bonus)
    if not (1 <= urgency <= 5 and 1 <= impact <= 5):
        raise ToolError("urgency/impact 须在 1-5 之间")

    score = urgency * impact + vip_bonus
    if score >= 20:
        level = "P0"
    elif score >= 12:
        level = "P1"
    elif score >= 6:
        level = "P2"
    else:
        level = "P3"

    return {
        "urgency": urgency,
        "impact": impact,
        "vip_bonus": vip_bonus,
        "score": score,
        "priority_level": level,
        "expression": f"{urgency} * {impact} + {vip_bonus}",
    }


def calculate(expression: str) -> dict[str, Any]:
    """安全数学计算（与 Day 19 calculate 同思路）。"""
    expression = expression.strip()
    if not expression:
        raise ToolError("expression 不能为空")
    if re.search(r"[a-zA-Z_]", expression):
        raise ToolError("表达式仅允许数字与运算符")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
    except SyntaxError as exc:
        raise ToolError(f"语法错误: {exc}") from exc

    display = str(int(result)) if result == int(result) else str(round(result, 4))
    return {"expression": expression, "result": display, "numeric": result}


def get_ticket_by_id(ticket_id: str) -> dict[str, Any]:
    """按 ID 查询 mock 工单。"""
    ticket_id = ticket_id.strip()
    tickets = _load_json(TICKETS_FILE)
    for t in tickets:
        if t["id"] == ticket_id:
            return t
    raise ToolError(f"工单 {ticket_id} 不存在")


# ReAct Action 名 → 函数
TOOL_REGISTRY: dict[str, Any] = {
    "classify_ticket": classify_ticket,
    "route_ticket": route_ticket,
    "search_kb_snippet": search_kb_snippet,
    "calc_priority_score": calc_priority_score,
    "calculate": calculate,
    "get_ticket_by_id": get_ticket_by_id,
}

TOOL_DESCRIPTIONS: dict[str, str] = {
    "classify_ticket": "分类工单意图。参数: text (str)",
    "route_ticket": "路由到技能组。参数: intent (str), customer_tier (str, 可选)",
    "search_kb_snippet": "检索知识库。参数: query (str), limit (int, 可选)",
    "calc_priority_score": "算优先级。参数: urgency (int), impact (int), vip_bonus (int, 可选)",
    "calculate": "数学计算。参数: expression (str)",
    "get_ticket_by_id": "查工单。参数: ticket_id (str)",
}


def run_tool(action: str, action_input: str | dict[str, Any]) -> str:
    """执行工具并返回 Observation 字符串。"""
    if action not in TOOL_REGISTRY:
        return json.dumps({"error": f"未知工具: {action}"}, ensure_ascii=False)

    fn = TOOL_REGISTRY[action]
    try:
        if isinstance(action_input, str):
            raw = action_input.strip()
            if raw.startswith("{"):
                params = json.loads(raw)
            else:
                # 单参数工具简写
                if action in ("classify_ticket", "search_kb_snippet", "calculate", "get_ticket_by_id"):
                    key = {
                        "classify_ticket": "text",
                        "search_kb_snippet": "query",
                        "calculate": "expression",
                        "get_ticket_by_id": "ticket_id",
                    }[action]
                    params = {key: raw}
                else:
                    params = {"intent": raw}
        else:
            params = action_input

        result = fn(**params) if isinstance(params, dict) else fn(params)
        return json.dumps(result, ensure_ascii=False)
    except (ToolError, TypeError, json.JSONDecodeError) as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


def format_tools_prompt() -> str:
    """生成 ReAct 系统提示中的工具列表。"""
    lines = []
    for name, desc in TOOL_DESCRIPTIONS.items():
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)


def main() -> None:
    print("=" * 60)
    print("Day 39 · tools_basic.py 演示")
    print("=" * 60)

    sample = "客户要求退款，订单已扣款但未到货，非常着急"
    print("\n[1] classify_ticket")
    print(json.dumps(classify_ticket(sample), ensure_ascii=False, indent=2))

    print("\n[2] route_ticket('refund', 'vip')")
    print(json.dumps(route_ticket("refund", "vip"), ensure_ascii=False, indent=2))

    print("\n[3] search_kb_snippet('退款政策')")
    print(json.dumps(search_kb_snippet("退款政策"), ensure_ascii=False, indent=2))

    print("\n[4] calc_priority_score(4, 5, 3)")
    print(json.dumps(calc_priority_score(4, 5, 3), ensure_ascii=False, indent=2))

    print("\n✅ tools_basic.py 完成")


if __name__ == "__main__":
    main()
