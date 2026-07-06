# -*- coding: utf-8 -*-
"""
Day 42 · Checkpointer 持久化演示

展示 LangGraph MemorySaver 如何按 thread_id 保存/恢复图状态。
无 API Key 时可独立运行。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

DATA_DIR = Path(__file__).resolve().parent / "data"
CHECKPOINT_LOG = DATA_DIR / "checkpoint_threads.json"


class CounterState(TypedDict):
    """计数器状态：演示跨 invoke 的持久化。"""

    count: int
    last_action: str


def increment_node(state: CounterState) -> dict:
    return {
        "count": state.get("count", 0) + 1,
        "last_action": "increment",
    }


def reset_node(state: CounterState) -> dict:
    return {"count": 0, "last_action": "reset"}


def build_counter_graph() -> StateGraph:
    graph = StateGraph(CounterState)
    graph.add_node("increment", increment_node)
    graph.add_node("reset", reset_node)
    graph.add_edge(START, "increment")
    graph.add_edge("increment", END)
    return graph


def compile_with_checkpointer(graph: StateGraph | None = None):
    g = graph or build_counter_graph()
    checkpointer = MemorySaver()
    return g.compile(checkpointer=checkpointer), checkpointer


def run_demo(thread_id: str = "demo-thread-1") -> dict:
    """同一 thread 连续 invoke，count 应累加。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    app, _ = compile_with_checkpointer()
    config = {"configurable": {"thread_id": thread_id}}

    results: list[dict] = []
    # 首次传入初始值；后续 invoke 空输入，从 checkpoint 恢复并继续累加
    out = app.invoke({"count": 0, "last_action": "init"}, config)
    results.append(dict(out))
    for _ in range(2):
        out = app.invoke({}, config)
        results.append(dict(out))

    snapshot = app.get_state(config)
    log = {
        "thread_id": thread_id,
        "invocations": results,
        "final_values": snapshot.values,
        "checkpoint_id": snapshot.config.get("configurable", {}).get("checkpoint_id"),
    }
    CHECKPOINT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    return log


def compare_threads() -> dict:
    """不同 thread_id 互不影响。"""
    app, _ = compile_with_checkpointer()
    cfg_a = {"configurable": {"thread_id": "thread-a"}}
    cfg_b = {"configurable": {"thread_id": "thread-b"}}

    app.invoke({"count": 0, "last_action": "init"}, cfg_a)
    app.invoke({}, cfg_a)
    app.invoke({"count": 0, "last_action": "init"}, cfg_b)

    state_a = app.get_state(cfg_a).values
    state_b = app.get_state(cfg_b).values
    return {"thread_a": state_a, "thread_b": state_b}


def main() -> None:
    print("=== Day 42 Checkpointer Demo ===\n")
    log = run_demo()
    print(f"thread_id={log['thread_id']}")
    for i, row in enumerate(log["invocations"], 1):
        print(f"  invoke #{i}: count={row['count']}")
    print(f"final count={log['final_values'].get('count')}")
    print(f"log -> {CHECKPOINT_LOG}\n")

    isolated = compare_threads()
    print("独立 thread 对比:")
    print(f"  thread-a count={isolated['thread_a'].get('count')}")
    print(f"  thread-b count={isolated['thread_b'].get('count')}")


if __name__ == "__main__":
    main()
