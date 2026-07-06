# -*- coding: utf-8 -*-
"""Pydantic schemas for office assistant API."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    mode: Literal["mock", "live"]
    agents: list[str]
    tools: list[str]


class TaskCreateRequest(BaseModel):
    request: str = Field(..., min_length=2, max_length=4000, description="用户办公任务描述")
    thread_id: Optional[str] = Field(None, max_length=64)


class ApprovalPayload(BaseModel):
    decision: Literal["approve", "reject"]
    comment: Optional[str] = Field(None, max_length=500)


class TaskResumeRequest(BaseModel):
    approval: ApprovalPayload


class AgentStep(BaseModel):
    agent: str
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)


class PendingApproval(BaseModel):
    action: str
    preview: dict[str, Any]
    reason: str


class TaskStateResponse(BaseModel):
    thread_id: str
    status: str
    user_request: str
    plan: list[str] = Field(default_factory=list)
    steps: list[AgentStep] = Field(default_factory=list)
    pending_approval: Optional[PendingApproval] = None
    result: Optional[dict[str, Any]] = None
    errors: list[str] = Field(default_factory=list)
    mode: Literal["mock", "live"]


class TaskCreateResponse(BaseModel):
    thread_id: str
    status: str
    message: str
    pending_approval: Optional[PendingApproval] = None
