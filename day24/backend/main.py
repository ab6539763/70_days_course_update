# -*- coding: utf-8 -*-
"""
Day 24 · 星火智服 Web ChatGPT Clone — FastAPI 入口

启动：
  cd day24 && uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .chat import get_llm_client, router as chat_router
from .database import init_db
from .schemas import HealthResponse


def _parse_cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:8080,http://localhost:8080,http://127.0.0.1:5500,http://localhost:5500",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="星火智服 Web Chat API",
    description="Day 24 · SSE 流式 + SQLite 会话持久化",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    client = get_llm_client()
    return HealthResponse(status="ok", mode=client.mode)  # type: ignore[arg-type]


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "xinghuo-web-chat",
        "docs": "/docs",
        "health": "/health",
        "chat_stream": "POST /api/chat/stream",
    }
