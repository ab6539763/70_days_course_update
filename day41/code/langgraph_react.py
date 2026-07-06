# -*- coding: utf-8 -*-
"""
Day 41 · LangGraph 版 ReAct 工单路由

将 Day 39 手写 ReAct 改写为 StateGraph。
"""

from __future__ import annotations

import importlib.util
import json
import operator
import sys
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

_WORKSPACE = Path(__file__).resolve().parents[2]
_CODE39 = _WORKSPACE / "day39" / "code"


def _load_module(name: str, path: Path):
    """按路径加载模块，避免与 day40 mock 冲突。"""
    parent = str(path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载 {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_day39_mock = _load_module("day39_mock_llm", _CODE39 / "mock_llm.py")
_day39_react = _load_module("day39_react_agent", _CODE39 / "react_agent.py")
_day39_tools = _load_module("day39_tools_basic", _CODE39 / "tools_basic.py")

ReActLLMClient = _day39_mock.ReActLLMClient
build_system_prompt = _day39_mock.build_system_prompt
parse_react_output = _day39_react.parse_react_output
format_tools_prompt = _day39_tools.format_tools_prompt
run_tool = _day39_tools.run_tool


class ReActState(TypedDict):
    """LangGraph 共享状态。"""

    messages: Annotated[list[dict[str, str]], operator.add]
    user_query: str
    step: int
    last_action: str
    last_observation: str
    final_answer: str
    done: bool


def reason_node(state: ReActState) -> dict[str, Any]:
    """推理节点：调用 LLM 生成 Thought/Action 或 Final Answer。"""
    llm = ReActLLMClient()
    system = build_system_prompt(format_tools_prompt())
    messages = [{"role": "system", "content": system}]
    messages.extend(state["messages"])
    if not any(m.get("role") == "user" for m in messages):
        messages.append({"role": "user", "content": state["user_query"]})

    response = llm.complete(messages)
    parsed = parse_react_output(response.text)

    if "final_answer" in parsed:
        return {
            "messages": [{"role": "assistant", "content": response.text}],
            "final_answer": parsed["final_answer"],
            "done": True,
            "step": state["step"] + 1,
        }

    return {
        "messages": [{"role": "assistant", "content": response.text}],
        "last_action": parsed.get("action", ""),
        "step": state["step"] + 1,
    }


def act_node(state: ReActState) -> dict[str, Any]:
    """行动节点：解析 Action 并执行工具。"""
    last_msg = state["messages"][-1]["content"]
    parsed = parse_react_output(last_msg)
    action = parsed.get("action") or state.get("last_action", "")
    action_input = parsed.get("action_input", "")

    if not action:
        return {"done": True, "final_answer": parsed.get("thought") or "无 Action"}

    observation = run_tool(action, action_input)
    return {
        "last_action": action,
        "last_observation": observation,
        "messages": [
            {
                "role": "assistant",
                "content": f"{last_msg.strip()}\n\nObservation: {observation}",
            }
        ],
    }


def should_continue(state: ReActState) -> Literal["act", "end"]:
    """条件边：是否继续循环。"""
    if state.get("done"):
        return "end"
    if state.get("step", 0) >= 6:
        return "end"
    last = state["messages"][-1]["content"] if state.get("messages") else ""
    if "Final Answer" in last:
        return "end"
    if parse_react_output(last).get("action"):
        return "act"
    return "end"


def build_react_graph() -> StateGraph:
    """构建 ReAct StateGraph。"""
    graph = StateGraph(ReActState)

    graph.add_node("reason", reason_node)
    graph.add_node("act", act_node)

    graph.set_entry_point("reason")
    graph.add_conditional_edges("reason", should_continue, {"act": "act", "end": END})
    graph.add_edge("act", "reason")

    return graph


def compile_react_agent():
    """编译为可执行 Runnable。"""
    return build_react_graph().compile()


def run_react_graph(query: str, *, verbose: bool = True) -> dict[str, Any]:
    """执行 LangGraph ReAct。"""
    app = compile_react_agent()
    init: ReActState = {
        "messages": [],
        "user_query": query,
        "step": 0,
        "last_action": "",
        "last_observation": "",
        "final_answer": "",
        "done": False,
    }
    final = app.invoke(init)

    if verbose:
        print(f"步数: {final.get('step')}")
        print(f"最终: {final.get('final_answer') or '(见 messages)'}")

    if not final.get("final_answer"):
        for msg in reversed(final.get("messages", [])):
            p = parse_react_output(msg.get("content", ""))
            if p.get("final_answer"):
                final["final_answer"] = p["final_answer"]
                break

    return final


def main() -> None:
    print("=" * 60)
    print("Day 41 · LangGraph ReAct")
    print("=" * 60)

    query = "VIP 客户投诉退款迟迟未到账，请分类并路由"
    print(f"\n>>> {query}\n")
    result = run_react_graph(query)
    print(
        f"\n结果:\n{json.dumps({k: result[k] for k in ('step', 'last_action', 'final_answer') if k in result}, ensure_ascii=False, indent=2)}"
    )
    print("\n✅ langgraph_react.py 完成")


if __name__ == "__main__":
    main()
