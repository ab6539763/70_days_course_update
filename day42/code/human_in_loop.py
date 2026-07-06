# -*- coding: utf-8 -*-
"""
Day 42 · Human-in-the-Loop：interrupt / resume

在 review 节点前中断，等待人工审批或修改后再 resume。
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from mock_llm import build_chat_model


class ReviewState(TypedDict):
    topic: str
    draft: str
    human_feedback: str
    approved: bool
    revision_count: int


def generate_draft(state: ReviewState) -> dict:
    llm = build_chat_model(
        responses=[f"[mock] 关于「{state['topic']}」的初稿：LangGraph 支持 interrupt 暂停图执行。"]
    )
    draft = llm.invoke(f"写一段关于 {state['topic']} 的短文").content
    return {"draft": str(draft), "revision_count": state.get("revision_count", 0)}


def human_review(state: ReviewState) -> dict:
    """interrupt 将控制权交还调用方，等待 Command(resume=...)。"""
    payload = {
        "draft": state["draft"],
        "topic": state["topic"],
        "hint": "resume 传 'approve' 通过，或传修改后的全文",
    }
    feedback = interrupt(payload)

    if str(feedback).strip().lower() == "approve":
        return {"approved": True, "human_feedback": "approved"}

    return {
        "draft": str(feedback),
        "approved": False,
        "human_feedback": str(feedback),
        "revision_count": state.get("revision_count", 0) + 1,
    }


def finalize(state: ReviewState) -> dict:
    status = "已发布" if state.get("approved") else "待修改"
    return {"draft": f"{state['draft']}\n\n---\n状态: {status}"}


def build_review_graph():
    graph = StateGraph(ReviewState)
    graph.add_node("generate", generate_draft)
    graph.add_node("review", human_review)
    graph.add_node("finalize", finalize)
    graph.add_edge(START, "generate")
    graph.add_edge("generate", "review")
    graph.add_edge("review", "finalize")
    graph.add_edge("finalize", END)
    return graph


def compile_review_app():
    return build_review_graph().compile(
        checkpointer=MemorySaver(),
        interrupt_before=["review"],
    )


def run_hitl_flow(
    topic: str = "Checkpointer 持久化",
    *,
    human_decision: str = "approve",
    thread_id: str = "hitl-demo",
) -> dict:
    """
    完整 HITL 流程：
    1. invoke 到 interrupt
    2. Command(resume=...) 继续
    """
    app = compile_review_app()
    config = {"configurable": {"thread_id": thread_id}}
    initial = {
        "topic": topic,
        "draft": "",
        "human_feedback": "",
        "approved": False,
        "revision_count": 0,
    }

    paused = app.invoke(initial, config)
    snapshot = app.get_state(config)
    pending_nodes = snapshot.next

    resumed = app.invoke(Command(resume=human_decision), config)
    return {
        "paused_state": dict(paused),
        "pending_nodes": pending_nodes,
        "final_state": dict(resumed),
    }


def main() -> None:
    print("=== Day 42 Human-in-the-Loop Demo ===\n")
    result = run_hitl_flow(human_decision="approve")
    print(f"interrupt 前 draft 长度: {len(result['paused_state'].get('draft', ''))}")
    print(f"pending nodes: {result['pending_nodes']}")
    final = result["final_state"]
    print(f"approved={final.get('approved')} revision_count={final.get('revision_count')}")
    print(f"draft 预览: {final.get('draft', '')[:120]}...")


if __name__ == "__main__":
    main()
