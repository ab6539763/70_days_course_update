# -*- coding: utf-8 -*-
"""
Day 42 · 写作 Agent 图：子图 + 并行节点 + 重试

主图：规划 → 并行调研（searcher + analyst）→ 写作 → 质检（可重试）
"""

from __future__ import annotations

import operator
import time
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from mock_llm import build_chat_model

MAX_WRITE_RETRIES = 3


class ResearchSubState(TypedDict):
    query: str
    notes: str


class WritingState(TypedDict):
    topic: str
    outline: str
    research_notes: Annotated[list[str], operator.add]
    draft: str
    quality_score: float
    retry_count: int
    status: str


def _research_subgraph():
    """子图：对单一路径做深度检索摘要。"""

    def collect(state: ResearchSubState) -> dict:
        note = f"[子图] 检索「{state['query']}」→ 命中 SparkTech 知识库 3 条"
        return {"notes": note}

    sg = StateGraph(ResearchSubState)
    sg.add_node("collect", collect)
    sg.add_edge(START, "collect")
    sg.add_edge("collect", END)
    return sg.compile()


RESEARCH_SUBGRAPH = _research_subgraph()


def plan_outline(state: WritingState) -> dict:
    llm = build_chat_model(
        responses=[f"[mock] 大纲：1.背景 2.{state['topic']}核心 3.实践 4.总结"]
    )
    outline = llm.invoke(f"为「{state['topic']}」列大纲").content
    return {"outline": str(outline), "status": "planned"}


def parallel_search(state: WritingState) -> dict:
    """并行节点 A：搜索型调研。"""
    time.sleep(0.01)
    sub_out = RESEARCH_SUBGRAPH.invoke(
        {"query": f"{state['topic']} 官方文档", "notes": ""}
    )
    return {"research_notes": [f"[searcher] {sub_out['notes']}"]}


def parallel_analyze(state: WritingState) -> dict:
    """并行节点 B：分析型调研。"""
    time.sleep(0.01)
    sub_out = RESEARCH_SUBGRAPH.invoke(
        {"query": f"{state['topic']} 最佳实践", "notes": ""}
    )
    return {"research_notes": [f"[analyst] {sub_out['notes']}"]}


def write_draft(state: WritingState) -> dict:
    llm = build_chat_model(
        responses=[
            f"[mock] 正文：{state['topic']} — 基于 {len(state.get('research_notes', []))} 条调研笔记撰写。"
        ]
    )
    notes_blob = "\n".join(state.get("research_notes", []))
    draft = llm.invoke(f"主题:{state['topic']}\n大纲:{state['outline']}\n笔记:{notes_blob}").content
    retry = state.get("retry_count", 0)
    # 前两次故意低分，第三次通过 —— 演示重试环
    score = 0.4 if retry < 2 else 0.85
    return {
        "draft": str(draft),
        "quality_score": score,
        "status": "drafted",
    }


def quality_gate(state: WritingState) -> dict:
    passed = state.get("quality_score", 0) >= 0.8
    if passed:
        return {"status": "passed"}
    return {
        "retry_count": state.get("retry_count", 0) + 1,
        "status": "retry",
    }


def route_after_quality(state: WritingState) -> str:
    if state.get("status") == "passed":
        return "publish"
    if state.get("retry_count", 0) >= MAX_WRITE_RETRIES:
        return "publish"
    return "rewrite"


def publish(state: WritingState) -> dict:
    tag = "已发布" if state.get("quality_score", 0) >= 0.8 else "降级发布"
    return {"status": tag, "draft": f"{state['draft']}\n\n[{tag}]"}


def build_writing_graph() -> StateGraph:
    graph = StateGraph(WritingState)
    graph.add_node("plan", plan_outline)
    graph.add_node("search", parallel_search)
    graph.add_node("analyze", parallel_analyze)
    graph.add_node("write", write_draft)
    graph.add_node("quality", quality_gate)
    graph.add_node("publish", publish)

    graph.add_edge(START, "plan")
    # 并行 fan-out
    graph.add_edge("plan", "search")
    graph.add_edge("plan", "analyze")
    graph.add_edge("search", "write")
    graph.add_edge("analyze", "write")
    graph.add_edge("write", "quality")
    graph.add_conditional_edges(
        "quality",
        route_after_quality,
        {"rewrite": "write", "publish": "publish"},
    )
    graph.add_edge("publish", END)
    return graph


def compile_writing_app():
    return build_writing_graph().compile(checkpointer=MemorySaver())


def run_writing_agent(topic: str = "LangGraph 并行与子图", thread_id: str = "write-1") -> dict:
    app = compile_writing_app()
    config = {"configurable": {"thread_id": thread_id}}
    initial: WritingState = {
        "topic": topic,
        "outline": "",
        "research_notes": [],
        "draft": "",
        "quality_score": 0.0,
        "retry_count": 0,
        "status": "init",
    }
    result = app.invoke(initial, config)
    return dict(result)


def main() -> None:
    print("=== Day 42 Writing Agent Graph ===\n")
    out = run_writing_agent()
    print(f"topic: {out.get('topic')}")
    print(f"research_notes: {len(out.get('research_notes', []))}")
    print(f"retry_count: {out.get('retry_count')}")
    print(f"quality_score: {out.get('quality_score')}")
    print(f"status: {out.get('status')}")
    print(f"draft: {str(out.get('draft', ''))[:160]}...")


if __name__ == "__main__":
    main()
