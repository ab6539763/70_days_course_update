# -*- coding: utf-8 -*-
"""Day 56 · Mock vLLM OpenAI 兼容服务。"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="SparkTech Mock vLLM", version="0.1.0")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "sparktech-qwen-lora"
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float = 0.7


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    model: str
    choices: list[dict[str, Any]]


MOCK_REPLIES = {
    "退款": "您好，退款一般3-5个工作日到账，已为您加急。",
    "投诉": "非常抱歉给您带来不便，专员将在30分钟内联系您。",
}


def generate_reply(messages: list[ChatMessage]) -> str:
    user = ""
    for m in reversed(messages):
        if m.role == "user":
            user = m.content
            break
    for k, v in MOCK_REPLIES.items():
        if k in user:
            return v
    return "您好，我是星火智服微调客服模型，请问有什么可以帮您？"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "mock-vllm"}


@app.post("/v1/chat/completions")
def chat(req: ChatRequest) -> ChatResponse:
    if os.environ.get("SPARKTECH_MOCK_FAIL"):
        raise RuntimeError("simulated failure")
    time.sleep(0.05)
    text = generate_reply(req.messages)
    return ChatResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        model=req.model,
        choices=[{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8100)
