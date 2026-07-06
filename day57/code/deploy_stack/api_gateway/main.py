# -*- coding: utf-8 -*-
"""Day 57 · API 网关 — 路由到 vLLM。"""

from __future__ import annotations

import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SparkTech Deploy Gateway")
VLLM_BASE = os.environ.get("VLLM_BASE_URL", "http://127.0.0.1:8100")


class ChatRequest(BaseModel):
    message: str
    route: str = "finetuned"  # finetuned | rag | fallback


class ChatResponse(BaseModel):
    reply: str
    route: str
    backend: str


@app.get("/health")
def health():
    return {"status": "ok", "vllm": VLLM_BASE}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if req.route == "rag":
        return ChatResponse(
            reply="[RAG] 请查阅知识库政策文档（教学占位）",
            route="rag",
            backend="project2-placeholder",
        )
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                f"{VLLM_BASE}/v1/chat/completions",
                json={
                    "model": "sparktech-qwen-lora",
                    "messages": [{"role": "user", "content": req.message}],
                },
            )
            r.raise_for_status()
            data = r.json()
            text = data["choices"][0]["message"]["content"]
    except Exception as e:
        if os.environ.get("SPARKTECH_MOCK") == "1":
            text = f"[mock-gateway] {req.message}"
        else:
            raise HTTPException(502, str(e)) from e
    return ChatResponse(reply=text, route=req.route, backend="vllm")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8020)
