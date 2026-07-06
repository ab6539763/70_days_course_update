# -*- coding: utf-8 -*-
"""Day 23 · Pydantic 请求/响应模型（对齐 Day 22 前端契约）。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Message(BaseModel):
    """单条对话消息，供历史查询与扩展接口使用。"""

    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """POST /api/chat 请求体 —— 与 day22/static/app.js fetchChat 对齐。"""

    message: str = Field(..., min_length=1, max_length=2000, description="用户本轮输入")
    session_id: str = Field(
        default="web-demo-001",
        min_length=1,
        max_length=128,
        description="会话 ID，服务端按此维护多轮上下文",
    )
    stream: bool = Field(
        default=False,
        description="是否流式；Day 23 仅实现非流式，流式留 Day 24+",
    )

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("message 不能为空白")
        return stripped


class ChatResponse(BaseModel):
    """POST /api/chat 响应体 —— 前端 typewriterEffect 读取 reply 字段。"""

    reply: str = Field(..., description="助手自然语言回复")
    session_id: str = Field(..., description="回显会话 ID")
    tools_used: list[str] = Field(
        default_factory=list,
        description="本轮调用的工具名列表，如 get_weather",
    )


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str = "ok"
    mode: str = "mock"
    version: str = "day23"
