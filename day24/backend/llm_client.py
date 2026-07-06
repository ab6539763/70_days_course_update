# -*- coding: utf-8 -*-
"""
Day 24 · LLM 客户端（mock / live）

- 无 API Key 时自动 mock，按关键词返回星火智服业务文案
- stream_chat() 以 Generator 逐块 yield，供 SSE 端点消费
"""

from __future__ import annotations

import json
import os
import re
import time
from collections.abc import Generator, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore[assignment]


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
ENV_API_KEY = "OPENAI_API_KEY"
ENV_BASE_URL = "OPENAI_BASE_URL"
ENV_MODEL = "OPENAI_MODEL"
ENV_FORCE_MOCK = "SPARKTECH_MOCK"

SYSTEM_PROMPT = """你是星火智服（SparkTech）智能客服助手。
回答简洁友好，使用中文。可帮用户查询天气、订单状态，或进行日常问候。"""


@dataclass
class ChatResult:
    """完整回复结果。"""

    text: str
    mode: str
    tools_used: list[str]


class LLMClientError(RuntimeError):
    pass


def _load_env() -> None:
    if load_dotenv is None:
        return
    backend_dir = Path(__file__).resolve().parent
    for candidate in (backend_dir / ".env", backend_dir.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()


def _extract_city(text: str) -> str:
    for marker in ("天气", "气温", "温度"):
        if marker in text:
            idx = text.index(marker)
            prefix = text[:idx]
            city = re.sub(r"[查的帮我一下怎样如何\s]", "", prefix)
            if len(city) >= 2:
                return city[-6:]
    return "上海"


def _extract_order_id(text: str) -> str:
    match = re.search(r"ST-?\d+", text, re.IGNORECASE)
    if match:
        raw = match.group(0).upper()
        return raw if raw.startswith("ST-") else f"ST-{raw[2:]}"
    return "ST-10086"


def _mock_plan(user_text: str) -> tuple[str, list[str]]:
    """启发式 mock，与 Day 22 前端 MOCK_RESPONSES 对齐。"""
    text = user_text.strip()
    lower = text.lower()

    if any(k in text for k in ("天气", "气温", "温度", "下雨")):
        city = _extract_city(text)
        reply = (
            f"{city}当前天气：晴，26°C，湿度 58%。"
            f"（数据来源：mock_weather_api）"
        )
        return reply, ["get_weather"]

    if any(k in text for k in ("订单", "物流")) or re.search(r"ST-?\d+", text, re.I):
        order_id = _extract_order_id(text)
        reply = (
            f"订单 {order_id}：已发货，承运 顺丰，预计 2026-07-08 送达。"
        )
        return reply, ["lookup_order"]

    if any(k in lower for k in ("你好", "您好", "hello", "hi")):
        return "您好！很高兴为您服务，请问有什么可以帮您？", []

    if any(k in text for k in ("帮助", "help")):
        reply = (
            "我可以帮您：\n"
            "1. 查询天气（例：上海天气）\n"
            "2. 查询订单（例：ST-10086）\n"
            "3. 日常问候"
        )
        return reply, []

    return (
        "已收到您的消息。当前为 mock 模式演示，"
        "请尝试包含「天气」「订单」或「你好」等关键词。"
        "配置 OPENAI_API_KEY 后可切换 live 模式。",
        [],
    )


def _chunk_text(text: str, chunk_size: int = 3) -> list[str]:
    chunks: list[str] = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return chunks or [""]


class SparkLLMClient:
    """星火智服 Web Chat 用 LLM 客户端。"""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
        mock_chunk_delay_ms: float = 35.0,
    ) -> None:
        _load_env()
        force_mock = os.getenv(ENV_FORCE_MOCK, "").strip().lower() in {"1", "true", "yes"}
        resolved_key = (api_key or os.getenv(ENV_API_KEY) or "").strip()
        self._api_key = "" if force_mock else resolved_key
        self._base_url = (base_url or os.getenv(ENV_BASE_URL) or DEFAULT_BASE_URL).rstrip("/")
        self._model = model or os.getenv(ENV_MODEL) or DEFAULT_MODEL
        self._timeout = timeout
        self._mock_chunk_delay_ms = mock_chunk_delay_ms

    @property
    def mode(self) -> str:
        return "mock" if self.is_mock_mode else "live"

    @property
    def is_mock_mode(self) -> bool:
        return not self._api_key

    def build_messages(self, history: list[dict[str, str]], user_text: str) -> list[dict[str, str]]:
        """组装 OpenAI 格式 messages。"""
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        for item in history:
            role = item.get("role", "")
            content = item.get("content", "")
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_text})
        return messages

    def chat(self, history: list[dict[str, str]], user_text: str) -> ChatResult:
        """非流式完整回复。"""
        full = "".join(self.stream_chat(history, user_text))
        # tools_used 仅在 mock 规划阶段可知，重新跑一次规划（轻量）
        if self.is_mock_mode:
            _, tools = _mock_plan(user_text)
            return ChatResult(text=full, mode="mock", tools_used=tools)
        return ChatResult(text=full, mode="live", tools_used=[])

    def stream_chat(
        self,
        history: list[dict[str, str]],
        user_text: str,
    ) -> Generator[str, None, None]:
        """逐块 yield 文本片段。"""
        if self.is_mock_mode:
            yield from self._mock_stream(user_text)
            return
        yield from self._live_stream(history, user_text)

    def _mock_stream(self, user_text: str) -> Iterator[str]:
        reply, _tools = _mock_plan(user_text)
        delay_sec = self._mock_chunk_delay_ms / 1000.0
        for chunk in _chunk_text(reply, chunk_size=2):
            time.sleep(delay_sec)
            yield chunk

    def _live_stream(self, history: list[dict[str, str]], user_text: str) -> Iterator[str]:
        if httpx is None:
            raise LLMClientError("未安装 httpx，无法 live 流式调用")

        messages = self.build_messages(history, user_text)
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": True,
            "temperature": 0.3,
        }

        with httpx.Client(timeout=self._timeout) as client:
            with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code >= 400:
                    body = response.read().decode(errors="replace")
                    raise LLMClientError(f"HTTP {response.status_code}: {body[:300]}")

                for line in response.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    choices = data.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    content = delta.get("content")
                    if content:
                        yield content
