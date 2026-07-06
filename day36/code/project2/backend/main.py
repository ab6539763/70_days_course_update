# -*- coding: utf-8 -*-
"""
Project 2 · 企业级知识库问答系统 — FastAPI 入口

启动：
  cd day36/code/project2 && uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .database import get_db, init_db
from .document_ingest import ingest_bytes, ingest_directory, rebuild_index
from .models import ChatMessage, ChatSession, DocumentRecord, KnowledgeChunk
from .rag_service import (
    RAGServiceError,
    citations_from_json,
    citations_to_json,
    get_rag_service,
)
from .schemas import (
    ChatRequest,
    ChatResponse,
    DocumentListResponse,
    DocumentOut,
    HealthResponse,
    HistoryResponse,
    MessageOut,
    RebuildResponse,
    StreamEvent,
    UploadResponse,
)

def _parse_cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:8080,http://localhost:8080,http://127.0.0.1:5500,http://localhost:5500",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    from .database import SessionLocal

    db = SessionLocal()
    try:
        ingest_directory(db)
        rag = get_rag_service()
        rag.load_index(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="星火智服 · 企业知识库问答 API",
    description="Project 2 · Hybrid RAG + 引用 + SSE",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ensure_session(db: Session, session_id: str) -> ChatSession:
    session = db.get(ChatSession, session_id)
    if session is None:
        session = ChatSession(id=session_id)
        db.add(session)
        db.flush()
    return session


def _save_message(
    db: Session,
    *,
    session_id: str,
    role: str,
    content: str,
    citations: list | None = None,
) -> ChatMessage:
    _ensure_session(db, session_id)
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        citations_json=citations_to_json(citations) if citations else None,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def _doc_to_out(doc: DocumentRecord) -> DocumentOut:
    return DocumentOut(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        char_count=doc.char_count,
        chunk_count=doc.chunk_count,
        status=doc.status,
        created_at=doc.created_at,
    )


@app.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    rag = get_rag_service()
    doc_count = db.query(DocumentRecord).count()
    chunk_count = db.query(KnowledgeChunk).count()
    if rag.chunk_count == 0 and chunk_count > 0:
        rag.load_index(db)
    return HealthResponse(
        status="ok",
        mode=rag.mode,  # type: ignore[arg-type]
        document_count=doc_count,
        chunk_count=chunk_count,
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "sparktech-kb-qa",
        "docs": "/docs",
        "health": "/health",
        "chat_stream": "POST /api/chat/stream",
        "upload": "POST /api/documents/upload",
    }


@app.get("/api/documents", response_model=DocumentListResponse)
def list_documents(db: Session = Depends(get_db)) -> DocumentListResponse:
    rows = db.query(DocumentRecord).order_by(DocumentRecord.id.desc()).all()
    docs = [_doc_to_out(r) for r in rows]
    return DocumentListResponse(documents=docs, total=len(docs))


@app.post("/api/documents/upload", response_model=UploadResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="请至少上传一个文件")

    uploaded: list[DocumentOut] = []
    total_chunks = 0
    for uf in files:
        content = await uf.read()
        if not content:
            continue
        try:
            result = ingest_bytes(db, uf.filename or "unknown.txt", content)
            uploaded.append(_doc_to_out(result.document))
            total_chunks += len(result.chunks)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    rag = get_rag_service()
    rag.load_index(db)
    return UploadResponse(
        uploaded=uploaded,
        rebuilt_chunks=total_chunks,
        message=f"成功上传 {len(uploaded)} 个文档",
    )


@app.post("/api/kb/rebuild", response_model=RebuildResponse)
def rebuild_kb(db: Session = Depends(get_db)) -> RebuildResponse:
    doc_count, chunk_count = rebuild_index(db)
    rag = get_rag_service()
    rag.load_index(db)
    return RebuildResponse(
        document_count=doc_count,
        chunk_count=chunk_count,
        message="知识库索引已重建",
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat_ask(body: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    _save_message(db, session_id=body.session_id, role="user", content=body.message)
    rag = get_rag_service()
    try:
        result = rag.ask(db, body.message)
    except RAGServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    saved = _save_message(
        db,
        session_id=body.session_id,
        role="assistant",
        content=result.text,
        citations=result.citations,
    )
    return ChatResponse(
        reply=result.text,
        session_id=body.session_id,
        mode=result.mode,  # type: ignore[arg-type]
        citations=result.citations,
        message_id=saved.id,
    )


@app.post("/api/chat/stream")
def chat_stream(body: ChatRequest, db: Session = Depends(get_db)) -> StreamingResponse:
    _save_message(db, session_id=body.session_id, role="user", content=body.message)
    rag = get_rag_service()
    session_id = body.session_id

    def event_generator():
        parts: list[str] = []
        citations = []
        mode = rag.mode

        try:
            for event_type, cites, delta in rag.stream_answer(db, body.message):
                if event_type == "citations" and cites is not None:
                    citations = cites
                    evt = StreamEvent(
                        event="citations",
                        session_id=session_id,
                        mode=mode,  # type: ignore[arg-type]
                        citations=cites,
                    )
                    yield f"data: {evt.model_dump_json()}\n\n"
                elif event_type == "delta" and delta:
                    parts.append(delta)
                    evt = StreamEvent(
                        event="delta",
                        delta=delta,
                        session_id=session_id,
                        mode=mode,  # type: ignore[arg-type]
                    )
                    yield f"data: {evt.model_dump_json()}\n\n"
                elif event_type == "done":
                    full_text = "".join(parts)
                    saved = _save_message(
                        db,
                        session_id=session_id,
                        role="assistant",
                        content=full_text,
                        citations=citations,
                    )
                    evt = StreamEvent(
                        event="done",
                        session_id=session_id,
                        mode=mode,  # type: ignore[arg-type]
                        citations=citations,
                        message_id=saved.id,
                    )
                    yield f"data: {evt.model_dump_json()}\n\n"
        except RAGServiceError as exc:
            err = StreamEvent(event="error", error=str(exc), session_id=session_id)
            yield f"data: {err.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/sessions/{session_id}/history", response_model=HistoryResponse)
def get_history(session_id: str, db: Session = Depends(get_db)) -> HistoryResponse:
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )
    messages = [
        MessageOut(
            id=row.id,
            role=row.role,  # type: ignore[arg-type]
            content=row.content,
            citations=citations_from_json(row.citations_json),
            created_at=row.created_at,
        )
        for row in rows
        if row.role in {"user", "assistant"}
    ]
    return HistoryResponse(session_id=session_id, messages=messages, count=len(messages))


@app.delete("/api/sessions/{session_id}")
def clear_session(session_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
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
