# -*- coding: utf-8 -*-
"""LangGraph state definition."""

from __future__ import annotations

from typing import Annotated, Any, Optional, TypedDict

from langgraph.graph.message import add_messages


class OfficeState(TypedDict, total=False):
    thread_id: str
    user_request: str
    plan: list[str]
    steps: list[dict[str, Any]]
    research_summary: str
    draft_id: str
    email_preview: dict[str, Any]
    calendar_preview: Optional[dict[str, Any]]
    pending_approval: Optional[dict[str, Any]]
    approval_decision: Optional[str]
    approval_comment: Optional[str]
    status: str
    result: Optional[dict[str, Any]]
    errors: list[str]
    messages: Annotated[list[Any], add_messages]
