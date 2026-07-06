# -*- coding: utf-8 -*-
"""FastAPI entry for Project 3 multi-agent office assistant."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.config import ensure_dirs, is_mock_mode
from backend.schemas import (
    HealthResponse,
    PendingApproval,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskResumeRequest,
    TaskStateResponse,
)
from graph.office_graph import get_office_graph
from tools import TOOL_REGISTRY
from tools.document_rag import build_rag_index


def _parse_cors_origins() -> list[str]:
    import os

    raw = os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:8088,http://localhost:8088,http://127.0.0.1:5500",
    )
    return [o.strip() for o in raw.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_dirs()
    build_rag_index()
    yield


app = FastAPI(
    title="星火智服 · 多 Agent 智能办公助手",
    description="Project 3 · LangGraph + Human-in-the-loop",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_task_response(state: dict) -> TaskStateResponse:
    pending = state.get("pending_approval")
    pa = PendingApproval(**pending) if pending else None
    return TaskStateResponse(
        thread_id=state["thread_id"],
        status=state["status"],
        user_request=state.get("user_request", ""),
        plan=state.get("plan") or [],
        steps=state.get("steps") or [],
        pending_approval=pa,
        result=state.get("result"),
        errors=state.get("errors") or [],
        mode="mock" if is_mock_mode() else "live",
    )


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        mode="mock" if is_mock_mode() else "live",
        agents=["planner", "researcher", "writer", "executor"],
        tools=sorted(TOOL_REGISTRY.keys()),
    )


@app.post("/api/tasks", response_model=TaskCreateResponse)
def create_task(body: TaskCreateRequest) -> TaskCreateResponse:
    svc = get_office_graph()
    state = svc.start_task(body.request.strip(), body.thread_id)
    pending = state.get("pending_approval")
    pa = PendingApproval(**pending) if pending else None
    msg = "任务已编排至人工审批节点" if pa else "任务已完成"
    return TaskCreateResponse(
        thread_id=state["thread_id"],
        status=state["status"],
        message=msg,
        pending_approval=pa,
    )


@app.get("/api/tasks/{thread_id}", response_model=TaskStateResponse)
def get_task(thread_id: str) -> TaskStateResponse:
    svc = get_office_graph()
    state = svc.get_state(thread_id)
    if not state:
        raise HTTPException(status_code=404, detail="thread not found")
    return _to_task_response(state)


@app.post("/api/tasks/{thread_id}/resume", response_model=TaskStateResponse)
def resume_task(thread_id: str, body: TaskResumeRequest) -> TaskStateResponse:
    svc = get_office_graph()
    current = svc.get_state(thread_id)
    if not current:
        raise HTTPException(status_code=404, detail="thread not found")
    if current.get("status") not in {"awaiting_approval", "approved"} and not svc.list_interrupt(thread_id):
        if current.get("status") in {"completed", "rejected"}:
            raise HTTPException(status_code=409, detail=f"task already {current['status']}")
    approval = body.approval.model_dump()
    state = svc.resume_task(thread_id, approval)
    return _to_task_response(state)


@app.get("/api/tasks/{thread_id}/interrupt")
def get_interrupt(thread_id: str):
    svc = get_office_graph()
    info = svc.list_interrupt(thread_id)
    if not info:
        raise HTTPException(status_code=404, detail="no pending interrupt")
    return info
