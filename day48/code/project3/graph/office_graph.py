# -*- coding: utf-8 -*-
"""
LangGraph 编排 — Planner → Researcher → Writer → Human Gate → Executor

特性：
- MemorySaver checkpointer 支持 interrupt / resume
- 敏感动作（发邮件、建日程）需人工审批
"""

from __future__ import annotations

import uuid
from functools import lru_cache
from typing import Any, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command, interrupt

from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from graph.state import OfficeState
from tools.calendar import calendar_schedule
from tools.email_tool import email_send


def _append_step(state: OfficeState, step: dict[str, Any]) -> list[dict[str, Any]]:
    steps = list(state.get("steps") or [])
    steps.append(step)
    return steps


def planner_node(state: OfficeState) -> dict[str, Any]:
    agent = PlannerAgent()
    out = agent.run(state["user_request"])
    step = {"agent": agent.name, "summary": out["summary"], "details": out["details"]}
    return {
        "plan": out["plan"],
        "steps": _append_step(state, step),
        "status": "planned",
    }


def researcher_node(state: OfficeState) -> dict[str, Any]:
    agent = ResearcherAgent()
    out = agent.run(state["user_request"], state.get("plan") or [])
    step = {"agent": agent.name, "summary": out["summary"], "details": out["details"]}
    return {
        "research_summary": out["summary"],
        "steps": _append_step(state, step),
        "status": "researched",
    }


def writer_node(state: OfficeState) -> dict[str, Any]:
    agent = WriterAgent()
    out = agent.run(state["user_request"], state.get("research_summary", ""))
    step = {"agent": agent.name, "summary": out["summary"], "details": out["details"]}
    pending = {
        "action": "send_email_and_optional_calendar",
        "preview": {
            "email": out["email_preview"],
            "calendar": out.get("details", {}).get("calendar_preview"),
        },
        "reason": "外发邮件与创建日程属于敏感操作，需人工确认",
    }
    return {
        "draft_id": out["draft_id"],
        "email_preview": out["email_preview"],
        "calendar_preview": out.get("details", {}).get("calendar_preview"),
        "pending_approval": pending,
        "steps": _append_step(state, step),
        "status": "awaiting_approval",
    }


def human_gate_node(state: OfficeState) -> dict[str, Any]:
    """LangGraph interrupt — 等待人工审批。"""
    payload = state.get("pending_approval") or {}
    decision = interrupt(
        {
            "type": "human_approval",
            "thread_id": state.get("thread_id"),
            "action": payload.get("action"),
            "preview": payload.get("preview"),
            "reason": payload.get("reason"),
        }
    )
    if isinstance(decision, dict):
        approved = decision.get("decision") == "approve"
        comment = decision.get("comment")
    else:
        approved = str(decision).lower() in {"approve", "approved", "yes", "true"}
        comment = None

    if not approved:
        return {
            "approval_decision": "reject",
            "approval_comment": comment,
            "status": "rejected",
            "result": {"message": "用户拒绝发送，流程已终止"},
        }
    return {
        "approval_decision": "approve",
        "approval_comment": comment,
        "status": "approved",
    }


def executor_node(state: OfficeState) -> dict[str, Any]:
    draft_id = state.get("draft_id", "")
    send_result = email_send(draft_id)
    calendar_result = None
    cal = state.get("calendar_preview")
    if cal:
        calendar_result = calendar_schedule(
            title=cal["title"],
            start=cal["start"],
            end=cal["end"],
            attendees=cal.get("attendees"),
            location=cal.get("location", "3F 会议室 A"),
        )
    step = {
        "agent": "executor",
        "summary": "已执行审批通过的动作",
        "details": {"email_send": send_result, "calendar": calendar_result},
    }
    return {
        "steps": _append_step(state, step),
        "status": "completed",
        "result": {
            "email": send_result,
            "calendar": calendar_result,
            "message": "办公任务执行完成",
        },
        "pending_approval": None,
    }


def route_after_gate(state: OfficeState) -> Literal["executor", "end"]:
    if state.get("approval_decision") == "approve":
        return "executor"
    return "end"


def build_office_graph():
    graph = StateGraph(OfficeState)
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("human_gate", human_gate_node)
    graph.add_node("executor", executor_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "human_gate")
    graph.add_conditional_edges("human_gate", route_after_gate, {"executor": "executor", "end": END})
    graph.add_edge("executor", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer, interrupt_before=[])


class OfficeGraphService:
    def __init__(self) -> None:
        self._graph = build_office_graph()

    @property
    def graph(self):
        return self._graph

    def _config(self, thread_id: str) -> dict[str, Any]:
        return {"configurable": {"thread_id": thread_id}}

    def start_task(self, user_request: str, thread_id: str | None = None) -> dict[str, Any]:
        tid = thread_id or str(uuid.uuid4())
        initial: OfficeState = {
            "thread_id": tid,
            "user_request": user_request,
            "plan": [],
            "steps": [],
            "errors": [],
            "status": "started",
        }
        result = self._graph.invoke(initial, self._config(tid))
        return self._public_state(result)

    def resume_task(self, thread_id: str, approval: dict[str, Any]) -> dict[str, Any]:
        result = self._graph.invoke(Command(resume=approval), self._config(thread_id))
        return self._public_state(result)

    def get_state(self, thread_id: str) -> dict[str, Any] | None:
        snap = self._graph.get_state(self._config(thread_id))
        if not snap or not snap.values:
            return None
        return self._public_state(snap.values)

    def list_interrupt(self, thread_id: str) -> dict[str, Any] | None:
        snap = self._graph.get_state(self._config(thread_id))
        if not snap:
            return None
        if snap.next:
            return {
                "thread_id": thread_id,
                "next_nodes": list(snap.next),
                "pending": snap.values.get("pending_approval"),
            }
        return None

    @staticmethod
    def _public_state(state: dict[str, Any]) -> dict[str, Any]:
        return {
            "thread_id": state.get("thread_id", ""),
            "status": state.get("status", "unknown"),
            "user_request": state.get("user_request", ""),
            "plan": state.get("plan") or [],
            "steps": state.get("steps") or [],
            "pending_approval": state.get("pending_approval"),
            "result": state.get("result"),
            "errors": state.get("errors") or [],
            "approval_decision": state.get("approval_decision"),
        }


@lru_cache(maxsize=1)
def get_office_graph() -> OfficeGraphService:
    return OfficeGraphService()
