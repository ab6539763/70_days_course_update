# -*- coding: utf-8 -*-
"""Project 3 验收脚本 — Agent、工具、LangGraph interrupt/resume、API。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["SPARKTECH_MOCK"] = "1"

from fastapi.testclient import TestClient  # noqa: E402

from agents import PlannerAgent, ResearcherAgent, WriterAgent  # noqa: E402
from backend.main import app  # noqa: E402
from graph.office_graph import OfficeGraphService  # noqa: E402
from tools import TOOL_REGISTRY  # noqa: E402
from tools.calendar import calendar_list, calendar_schedule, reset_calendar_store  # noqa: E402
from tools.document_rag import build_rag_index, document_rag_search, reset_rag_index  # noqa: E402
from tools.email_tool import email_draft, email_send, reset_email_store  # noqa: E402
from tools.task_list import reset_task_store, task_list_add  # noqa: E402
from tools.web_search import web_search  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_tools_registry() -> None:
    names = set(TOOL_REGISTRY.keys())
    required = {
        "calendar_list",
        "calendar_schedule",
        "email_draft",
        "email_send",
        "web_search",
        "document_rag_search",
        "task_list_add",
        "task_list_list",
    }
    if not required.issubset(names):
        fail(f"工具缺失: {required - names}")
    ok(f"tools registry ({len(names)} tools)")


def test_individual_tools() -> None:
    reset_email_store()
    reset_calendar_store()
    reset_task_store()
    reset_rag_index()
    build_rag_index()

    rag = document_rag_search("退款 7 天")
    assert rag["hits"], "RAG 应命中样本"
    web = web_search("办公自动化")
    assert web["results"]
    cal = calendar_list()
    assert cal["events"]
    draft = email_draft(["a@x.com"], "主题", "正文")
    sent = email_send(draft["draft"]["draft_id"])
    assert sent["status"] == "sent"
    sched = calendar_schedule("评审会", "2026-07-08T10:00:00+08:00", "2026-07-08T11:00:00+08:00")
    assert sched["status"] == "scheduled"
    task = task_list_add("整理答辩材料")
    assert task["task"]["id"]
    ok("individual tools mock execution")


def test_agents_pipeline() -> None:
    req = "请调研退款政策并起草通知邮件，安排周三产品会议"
    planner = PlannerAgent().run(req)
    assert len(planner["plan"]) >= 2
    researcher = ResearcherAgent().run(req, planner["plan"])
    assert "调研" in researcher["summary"] or "内部" in researcher["summary"]
    writer = WriterAgent().run(req, researcher["summary"])
    assert writer["draft_id"]
    ok("planner → researcher → writer agents")


def test_graph_interrupt_resume() -> None:
    svc = OfficeGraphService()
    state = svc.start_task("请根据退款制度起草客户通知邮件并预约会议")
    assert state["status"] == "awaiting_approval"
    assert state["pending_approval"]
    assert len(state["steps"]) >= 3

    resumed = svc.resume_task(
        state["thread_id"],
        {"decision": "approve", "comment": "verify auto-approve"},
    )
    assert resumed["status"] == "completed"
    assert resumed["result"]
    ok("LangGraph interrupt + resume (approve)")


def test_graph_reject() -> None:
    svc = OfficeGraphService()
    state = svc.start_task("起草一封测试拒绝邮件")
    resumed = svc.resume_task(state["thread_id"], {"decision": "reject"})
    assert resumed["status"] == "rejected"
    ok("LangGraph resume (reject)")


def test_api_health_and_task_flow() -> None:
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        data = health.json()
        assert data["mode"] == "mock"
        assert len(data["agents"]) >= 3
        assert len(data["tools"]) >= 5

        created = client.post(
            "/api/tasks",
            json={"request": "请检索退款政策并起草邮件通知团队"},
        )
        assert created.status_code == 200
        body = created.json()
        tid = body["thread_id"]
        assert body["pending_approval"]

        got = client.get(f"/api/tasks/{tid}")
        assert got.status_code == 200
        assert got.json()["status"] == "awaiting_approval"

        resumed = client.post(
            f"/api/tasks/{tid}/resume",
            json={"approval": {"decision": "approve", "comment": "api verify"}},
        )
        assert resumed.status_code == 200
        final = resumed.json()
        assert final["status"] == "completed"
        assert final["result"]
    ok("FastAPI task create / get / resume")


def main() -> None:
    print("=== Project 3 verify ===")
    test_tools_registry()
    test_individual_tools()
    test_agents_pipeline()
    test_graph_interrupt_resume()
    test_graph_reject()
    test_api_health_and_task_flow()
    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
