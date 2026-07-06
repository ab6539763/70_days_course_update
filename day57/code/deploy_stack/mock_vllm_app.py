# -*- coding: utf-8 -*-
"""Docker 用 Mock vLLM — 精简版。"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    model: str = "sparktech-qwen-lora"
    messages: list[dict]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/chat/completions")
def chat(req: ChatRequest):
    user = req.messages[-1]["content"] if req.messages else ""
    text = "您好，Docker 内 mock vLLM 已收到：" + user[:50]
    return {
        "id": "mock",
        "choices": [{"message": {"role": "assistant", "content": text}}],
    }
