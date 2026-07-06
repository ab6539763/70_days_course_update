# -*- coding: utf-8 -*-
"""Day 56 · 调用 Mock vLLM（OpenAI 格式）。"""

from __future__ import annotations

import json
import os
import urllib.request


def chat_completion(prompt: str, *, base_url: str | None = None) -> str:
    base = base_url or os.environ.get("VLLM_BASE_URL", "http://127.0.0.1:8100")
    payload = {
        "model": "sparktech-qwen-lora",
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        f"{base}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def local_mock_chat(prompt: str) -> str:
    """无 server 时的离线 fallback。"""
    from mock_vllm_server import generate_reply, ChatMessage
    return generate_reply([ChatMessage(role="user", content=prompt)])


if __name__ == "__main__":
    print(local_mock_chat("我要退款"))
