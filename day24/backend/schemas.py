# -*- coding: utf-8 -*-
"""Day 24 · Pydantic 请求/响应模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """POST /api/chat 与 /api/chat/stream 请求体。"""

    message: str = Field(..., min_length=1, max_length=4000, description="用户输入")
    session_id: str = Field(..., min_length=1, max_length=64, description="会话 ID")
    stream: bool = Field(default=True, description="是否流式（stream 端点忽略此字段）")

    @field_validator("message", "session_id")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("不能为空或纯空格")
        return stripped


class ChatResponse(BaseModel):
    """非流式聊天响应。"""

    reply: str
    session_id: str
    mode: Literal["mock", "live"]
    tools_used: list[str] = Field(default_factory=list)
    message_id: int | None = None


class StreamDeltaEvent(BaseModel):
    """SSE data 行 JSON 结构。"""

    event: Literal["delta", "done", "error"] = "delta"
    delta: str = ""
    session_id: str | None = None
    mode: Literal["mock", "live"] | None = None
    tools_used: list[str] | None = None
    message_id: int | None = None
    error: str | None = None


class MessageOut(BaseModel):
    """历史消息输出。"""

    id: int
    role: str
    content: str
    tools_used: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    """GET /api/sessions/{session_id}/history 响应。"""

    session_id: str
    messages: list[MessageOut]
    count: int


class HealthResponse(BaseModel):
    """健康检查。"""

    status: str = "ok"
    mode: Literal["mock", "live"]
    database: str = "sqlite"
