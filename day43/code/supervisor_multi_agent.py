# -*- coding: utf-8 -*-
"""
Day 43 · Supervisor 多 Agent 研究团队

Supervisor 按阶段路由 Searcher → Analyst → Writer，最终输出研究报告。
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent_roles import (
    RESEARCH_TEAM,
    AgentResult,
    format_handoff,
    pick_next_agent_mock,
    run_agent,
)


class TeamState(TypedDict):
    task: str
    messages: list[str]
    search_result: str
    analysis_result: str
    report: str
    current_agent: str
    steps: int
    status: str


def supervisor_node(state: TeamState) -> dict:
    has_search = bool(state.get("search_result"))
    has_analysis = bool(state.get("analysis_result"))
    has_report = bool(state.get("report"))
    next_agent = pick_next_agent_mock(
        state.get("current_agent", ""),
        has_search,
        has_analysis,
        has_report,
    )
    log = f"[supervisor] route -> {next_agent} (step {state.get('steps', 0) + 1})"
    return {
        "current_agent": next_agent,
        "messages": state.get("messages", []) + [log],
        "steps": state.get("steps", 0) + 1,
    }


def _worker_node(agent_name: str):
    def node(state: TeamState) -> dict:
        context = format_handoff(_collect_prior(state))
        result = run_agent(agent_name, state["task"], context)
        updates: dict = {
            "messages": state.get("messages", []) + [f"[{agent_name}] done"],
            "current_agent": agent_name,
        }
        if agent_name == "searcher":
            updates["search_result"] = result.content
        elif agent_name == "analyst":
            updates["analysis_result"] = result.content
        elif agent_name == "writer":
            updates["report"] = result.content
            updates["status"] = "completed"
        return updates

    return node


def _collect_prior(state: TeamState) -> list[AgentResult]:
    out: list[AgentResult] = []
    if state.get("search_result"):
        out.append(AgentResult("searcher", state["search_result"]))
    if state.get("analysis_result"):
        out.append(AgentResult("analyst", state["analysis_result"]))
    return out


def route_from_supervisor(state: TeamState) -> str:
    agent = state.get("current_agent", "searcher")
    if agent == "FINISH":
        return "end"
    if agent in RESEARCH_TEAM:
        return agent
    return "end"


def finalize_node(state: TeamState) -> dict:
    report = state.get("report") or state.get("analysis_result") or state.get("search_result", "")
    return {"status": "finished", "report": report}


def build_supervisor_graph() -> StateGraph:
    graph = StateGraph(TeamState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("searcher", _worker_node("searcher"))
    graph.add_node("analyst", _worker_node("analyst"))
    graph.add_node("writer", _worker_node("writer"))
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "searcher": "searcher",
            "analyst": "analyst",
            "writer": "writer",
            "end": "finalize",
        },
    )
    for worker in ("searcher", "analyst", "writer"):
        graph.add_edge(worker, "supervisor")
    graph.add_edge("finalize", END)
    return graph


def compile_supervisor_app():
    return build_supervisor_graph().compile(checkpointer=MemorySaver())


def run_research_team(
    task: str = "调研 LangGraph Supervisor 多 Agent 模式",
    thread_id: str = "team-1",
) -> dict:
    app = compile_supervisor_app()
    config = {"configurable": {"thread_id": thread_id}}
    initial: TeamState = {
        "task": task,
        "messages": [],
        "search_result": "",
        "analysis_result": "",
        "report": "",
        "current_agent": "",
        "steps": 0,
        "status": "running",
    }
    return dict(app.invoke(initial, config))


def main() -> None:
    print("=== Day 43 Supervisor Multi-Agent ===\n")
    result = run_research_team()
    print(f"task: {result.get('task')}")
    print(f"steps: {result.get('steps')}")
    print(f"status: {result.get('status')}")
    print("\n--- messages ---")
    for m in result.get("messages", []):
        print(f"  {m}")
    print("\n--- report preview ---")
    print(str(result.get("report", ""))[:400])


if __name__ == "__main__":
    main()
