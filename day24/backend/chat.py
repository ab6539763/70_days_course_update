# -*- coding: utf-8 -*-
"""Day 24 · 聊天 API 路由：非流式、SSE 流式、历史记录。"""

from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .database import get_db
from .llm_client import LLMClientError, SparkLLMClient
from .models import ChatMessage, ChatSession
from .schemas import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    MessageOut,
    StreamDeltaEvent,
)

router = APIRouter(prefix="/api", tags=["chat"])

_llm_client: SparkLLMClient | None = None


def get_llm_client() -> SparkLLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = SparkLLMClient()
    return _llm_client


def _ensure_session(db: Session, session_id: str) -> ChatSession:
    session = db.get(ChatSession, session_id)
    if session is None:
        session = ChatSession(id=session_id)
        db.add(session)
        db.flush()
    return session


def _load_history(db: Session, session_id: str) -> list[dict[str, str]]:
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )
    history: list[dict[str, str]] = []
    for row in rows:
        if row.role in {"user", "assistant"}:
            history.append({"role": row.role, "content": row.content})
    return history


def _save_message(
    db: Session,
    *,
    session_id: str,
    role: str,
    content: str,
    tools_used: list[str] | None = None,
) -> ChatMessage:
    _ensure_session(db, session_id)
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        tools_used=json.dumps(tools_used or [], ensure_ascii=False) if tools_used else None,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def _parse_tools_used(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


@router.post("/chat", response_model=ChatResponse)
def chat_completion(
    body: ChatRequest,
    db: Session = Depends(get_db),
    llm: SparkLLMClient = Depends(get_llm_client),
) -> ChatResponse:
    """非流式聊天：等待完整回复后返回 JSON。"""
    _save_message(db, session_id=body.session_id, role="user", content=body.message)
    history = _load_history(db, body.session_id)
    # 去掉刚写入的当前 user 消息，避免重复
    if history and history[-1]["role"] == "user":
        history = history[:-1]

    try:
        result = llm.chat(history, body.message)
    except LLMClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    saved = _save_message(
        db,
        session_id=body.session_id,
        role="assistant",
        content=result.text,
        tools_used=result.tools_used,
    )
    return ChatResponse(
        reply=result.text,
        session_id=body.session_id,
        mode=result.mode,  # type: ignore[arg-type]
        tools_used=result.tools_used,
        message_id=saved.id,
    )


@router.post("/chat/stream")
def chat_stream(
    body: ChatRequest,
    db: Session = Depends(get_db),
    llm: SparkLLMClient = Depends(get_llm_client),
) -> StreamingResponse:
    """SSE 流式聊天：逐块推送 delta，结束时发送 done 事件。"""

    _save_message(db, session_id=body.session_id, role="user", content=body.message)
    history = _load_history(db, body.session_id)
    if history and history[-1]["role"] == "user":
        history = history[:-1]

    session_id = body.session_id
    user_message = body.message

    def event_generator() -> Iterator[str]:
        parts: list[str] = []
        tools_used: list[str] = []
        mode = llm.mode

        try:
            if llm.is_mock_mode:
                from .llm_client import _mock_plan

                _, tools_used = _mock_plan(user_message)

            for chunk in llm.stream_chat(history, user_message):
                parts.append(chunk)
                event = StreamDeltaEvent(
                    event="delta",
                    delta=chunk,
                    session_id=session_id,
                    mode=mode,  # type: ignore[arg-type]
                )
                yield f"data: {event.model_dump_json()}\n\n"

            full_text = "".join(parts)
            saved = _save_message(
                db,
                session_id=session_id,
                role="assistant",
                content=full_text,
                tools_used=tools_used,
            )
            done_event = StreamDeltaEvent(
                event="done",
                delta="",
                session_id=session_id,
                mode=mode,  # type: ignore[arg-type]
                tools_used=tools_used,
                message_id=saved.id,
            )
            yield f"data: {done_event.model_dump_json()}\n\n"
        except LLMClientError as exc:
            err_event = StreamDeltaEvent(
                event="error",
                error=str(exc),
                session_id=session_id,
            )
            yield f"data: {err_event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions/{session_id}/history", response_model=HistoryResponse)
def get_history(session_id: str, db: Session = Depends(get_db)) -> HistoryResponse:
    """获取会话历史（不含 system）。"""
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )
    messages = [
        MessageOut(
            id=row.id,
            role=row.role,
            content=row.content,
            tools_used=_parse_tools_used(row.tools_used),
            created_at=row.created_at,
        )
        for row in rows
        if row.role in {"user", "assistant"}
    ]
    return HistoryResponse(session_id=session_id, messages=messages, count=len(messages))


@router.delete("/sessions/{session_id}")
def clear_session(session_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """清空会话消息（保留 session 行）。"""
    session = db.get(ChatSession, session_id)
    if session is None:
        return {"status": "ok", "session_id": session_id, "cleared": "0"}

    count = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"status": "ok", "session_id": session_id, "cleared": str(count)}
