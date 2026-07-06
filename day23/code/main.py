# -*- coding: utf-8 -*-
"""
Day 23 · FastAPI Chat API

启动：
  cd day23/code
  uvicorn main:app --reload --host 127.0.0.1 --port 8000

文档：
  http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from chat_service import ChatService
from models import ChatRequest, ChatResponse, HealthResponse, Message

app = FastAPI(
    title="星火智服 API",
    description="Day 23 · FastAPI 入门 + Chat 非流式接口（对齐 Day 22 前端契约）",
    version="0.23.0",
)

# Day 24 联调：允许 day22 preview.sh (8080) 跨域访问 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_service = ChatService()


@app.get("/", tags=["入门"])
def root() -> dict[str, str]:
    """根路由：返回欢迎信息与文档入口。"""
    return {
        "service": "星火智服",
        "docs": "/docs",
        "health": "/health",
        "chat": "POST /api/chat",
    }


@app.get("/health", response_model=HealthResponse, tags=["入门"])
def health() -> HealthResponse:
    """健康检查 —— 运维与前端探活。"""
    return HealthResponse(status="ok", mode=chat_service.mode_label, version="day23")


@app.get("/items/{item_id}", tags=["入门"])
def read_item(
    item_id: int,
    q: str | None = Query(default=None, description="可选查询参数，如 ?q=spark"),
) -> dict[str, str | int | None]:
    """
    教学路由：路径参数 `item_id` + 查询参数 `q`。

    示例：GET /items/42?q=hello
    """
    return {"item_id": item_id, "q": q}


@app.get("/sessions/{session_id}/messages", response_model=list[Message], tags=["Chat"])
def list_session_messages(session_id: str) -> list[Message]:
    """按 session_id 查看当前会话消息（调试用）。"""
    session = chat_service.get_session(session_id)
    return session.to_message_models()


@app.delete("/sessions/{session_id}", tags=["Chat"])
def clear_session(session_id: str) -> dict[str, str]:
    """清空指定会话历史。"""
    chat_service.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
def api_chat(request: ChatRequest) -> ChatResponse:
    """
    非流式 Chat 接口 —— 与 day22/static/app.js `fetchChat` 契约一致。

    请求体：
    ```json
    {"message": "查上海天气", "session_id": "web-demo-001", "stream": false}
    ```

    响应体：
    ```json
    {"reply": "...", "session_id": "web-demo-001", "tools_used": ["get_weather"]}
    ```
    """
    if request.stream:
        raise HTTPException(
            status_code=501,
            detail="Day 23 仅实现非流式；流式 SSE 见 Day 24+",
        )
    return chat_service.chat(request)
