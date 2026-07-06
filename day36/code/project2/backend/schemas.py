# -*- coding: utf-8 -*-
"""Pydantic 请求/响应模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    mode: Literal["mock", "live"]
    document_count: int = 0
    chunk_count: int = 0


class CitationOut(BaseModel):
    chunk_id: str
    source: str
    snippet: str
    score: float = 0.0
    chunk_index: int = 0


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(..., min_length=1, max_length=64)
    stream: bool = True


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    mode: Literal["mock", "live"]
    citations: list[CitationOut] = Field(default_factory=list)
    message_id: int | None = None


class MessageOut(BaseModel):
    id: int
    role: Literal["user", "assistant", "system"]
    content: str
    citations: list[CitationOut] = Field(default_factory=list)
    created_at: datetime


class HistoryResponse(BaseModel):
    session_id: str
    messages: list[MessageOut]
    count: int


class StreamEvent(BaseModel):
    event: Literal["delta", "citations", "done", "error"]
    delta: str = ""
    session_id: str = ""
    mode: Literal["mock", "live"] | None = None
    citations: list[CitationOut] = Field(default_factory=list)
    message_id: int | None = None
    error: str | None = None


class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    char_count: int
    chunk_count: int
    status: str
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentOut]
    total: int


class UploadResponse(BaseModel):
    uploaded: list[DocumentOut]
    rebuilt_chunks: int
    message: str


class RebuildResponse(BaseModel):
    document_count: int
    chunk_count: int
    message: str
