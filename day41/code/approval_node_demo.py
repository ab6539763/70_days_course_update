# -*- coding: utf-8 -*-
"""
Day 41 · 人工审批节点 Demo
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

_CODE39 = Path(__file__).resolve().parents[2] / "day39" / "code"


def _load_tools():
    spec = importlib.util.spec_from_file_location("day39_tools", _CODE39 / "tools_basic.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


_tools = _load_tools()
classify_ticket = _tools.classify_ticket
route_ticket = _tools.route_ticket


class ApprovalState(TypedDict):
    ticket_text: str
    classification: dict[str, Any]
    route_result: dict[str, Any]
    needs_approval: bool
    approved: bool | None
    final_message: str


def classify_node(state: ApprovalState) -> dict[str, Any]:
    result = classify_ticket(state["ticket_text"])
    intent = result.get("intent", "general")
    needs = intent in ("complaint", "refund")
    return {"classification": result, "needs_approval": needs}


def approval_node(state: ApprovalState) -> dict[str, Any]:
    text = state["ticket_text"].lower()
    if "拒绝" in text or "reject" in text:
        approved = False
    elif "vip" in text or "加急" in text:
        approved = True
    else:
        approved = True
    return {"approved": approved}


def route_node(state: ApprovalState) -> dict[str, Any]:
    intent = state["classification"].get("intent", "general")
    tier = "vip" if "vip" in state["ticket_text"].lower() else "standard"
    return {"route_result": route_ticket(intent, tier)}


def reject_node(state: ApprovalState) -> dict[str, Any]:
    return {"final_message": "人工审批未通过，工单保持待处理状态，已通知值班主管。"}


def finalize_node(state: ApprovalState) -> dict[str, Any]:
    r = state.get("route_result", {})
    msg = (
        f"工单已路由至【{r.get('team_label', r.get('team'))}】，"
        f"SLA {r.get('sla_hours')} 小时。"
        f"（意图: {state['classification'].get('intent')}）"
    )
    return {"final_message": msg}


def after_classify(state: ApprovalState) -> Literal["approval", "route"]:
    if state.get("needs_approval"):
        return "approval"
    return "route"


def after_approval(state: ApprovalState) -> Literal["route", "reject"]:
    if state.get("approved"):
        return "route"
    return "reject"


def build_approval_graph() -> StateGraph:
    g = StateGraph(ApprovalState)
    g.add_node("classify", classify_node)
    g.add_node("approval", approval_node)
    g.add_node("route", route_node)
    g.add_node("reject", reject_node)
    g.add_node("finalize", finalize_node)

    g.set_entry_point("classify")
    g.add_conditional_edges("classify", after_classify, {"approval": "approval", "route": "route"})
    g.add_conditional_edges("approval", after_approval, {"route": "route", "reject": "reject"})
    g.add_edge("route", "finalize")
    g.add_edge("reject", END)
    g.add_edge("finalize", END)
    return g


def compile_with_memory():
    return build_approval_graph().compile(checkpointer=MemorySaver())


def run_demo(ticket_text: str) -> dict[str, Any]:
    app = build_approval_graph().compile()
    init: ApprovalState = {
        "ticket_text": ticket_text,
        "classification": {},
        "route_result": {},
        "needs_approval": False,
        "approved": None,
        "final_message": "",
    }
    return app.invoke(init)


def main() -> None:
    print("=" * 60)
    print("Day 41 · approval_node_demo")
    print("=" * 60)

    cases = [
        "一般咨询：如何修改收货地址",
        "VIP 客户投诉退款迟迟未到账，请加急",
        "客户明确拒绝自动路由，请人工处理",
    ]
    for text in cases:
        print(f"\n>>> {text}")
        out = run_demo(text)
        print(
            json.dumps(
                {
                    "intent": out.get("classification", {}).get("intent"),
                    "needs_approval": out.get("needs_approval"),
                    "approved": out.get("approved"),
                    "final": out.get("final_message"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    print("\n✅ approval_node_demo.py 完成")


if __name__ == "__main__":
    main()
