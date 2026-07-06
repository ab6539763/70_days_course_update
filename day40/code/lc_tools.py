# -*- coding: utf-8 -*-
"""
Day 40 · LangChain @tool 工具定义

星火智服 Phase3 工单路由工具（LangChain 版）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from langchain_core.tools import tool

# 复用 Day 39 业务逻辑
_CODE39 = Path(__file__).resolve().parents[2] / "day39" / "code"
if str(_CODE39) not in sys.path:
    sys.path.insert(0, str(_CODE39))

from tools_basic import (  # noqa: E402
    calc_priority_score as _calc_priority_score,
    calculate as _calculate,
    classify_ticket as _classify_ticket,
    route_ticket as _route_ticket,
    search_kb_snippet as _search_kb_snippet,
)


@tool
def classify_ticket(text: str) -> str:
    """对工单描述进行意图分类。输入工单全文，返回 JSON 字符串。"""
    return json.dumps(_classify_ticket(text), ensure_ascii=False)


@tool
def route_ticket(intent: str, customer_tier: str = "standard") -> str:
    """将分类后的意图路由到技能组。intent 如 refund/technical；customer_tier 如 vip/enterprise/standard。"""
    return json.dumps(_route_ticket(intent, customer_tier), ensure_ascii=False)


@tool
def search_kb(query: str, limit: int = 3) -> str:
    """检索企业知识库片段（概念对接 Day 36 RAG）。返回 JSON。"""
    return json.dumps(_search_kb_snippet(query, limit=limit), ensure_ascii=False)


@tool
def calc_priority(urgency: int, impact: int, vip_bonus: int = 0) -> str:
    """计算工单优先级分数。urgency 和 impact 均为 1-5。"""
    return json.dumps(_calc_priority_score(urgency, impact, vip_bonus), ensure_ascii=False)


@tool
def calculator(expression: str) -> str:
    """安全数学计算器，如 (4+5)*2。"""
    return json.dumps(_calculate(expression), ensure_ascii=False)


def get_ticket_routing_tools() -> list:
    """工单路由全套工具。"""
    return [classify_ticket, route_ticket, search_kb, calc_priority, calculator]


def get_search_calc_tools() -> list:
    """搜索 + 计算精简套装。"""
    return [search_kb, calculator, classify_ticket]


def main() -> None:
    print("=" * 60)
    print("Day 40 · lc_tools.py @tool 演示")
    print("=" * 60)
    for t in get_ticket_routing_tools():
        print(f"\n[{t.name}] {t.description}")
        if t.name == "classify_ticket":
            print(t.invoke({"text": "客户申请退款"}))
    print("\n✅ lc_tools.py 完成")


if __name__ == "__main__":
    main()
