# -*- coding: utf-8 -*-
"""Day 14 · LLM 客户端 —— Day 12/13 Chat Completions 模式 + mock 降级。"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sparktech.exceptions import ConfigError, SparkTechError
from sparktech.utils import get_env

try:
    from openai import APIError, OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[misc, assignment]
    APIError = Exception  # type: ignore[misc, assignment]


class LLMClientError(SparkTechError):
    """LLM 调用失败。"""

    def __init__(self, message: str, *, vendor: str = "openai") -> None:
        super().__init__(message, code="LLM_CLIENT_ERROR")
        self.vendor = vendor


@dataclass
class ChatCompletionResult:
    """一次 chat 调用的结构化返回。"""

    text: str
    model: str
    vendor: str = "openai"
    mock: bool = False
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class LLMClient:
    """
    多轮对话 LLM 客户端。

    - 无 API Key 或 SPARKTECH_MOCK=1 时进入 mock 模式（课堂默认）
    - 配置 OPENAI_API_KEY 后调用真实 Chat Completions API
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.7,
        force_mock: bool | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else get_env("OPENAI_API_KEY", default="")
        self._model = model or get_env("OPENAI_MODEL", default="gpt-4o-mini")
        self._base_url = base_url or get_env(
            "OPENAI_BASE_URL", default="https://api.openai.com/v1"
        )
        self._temperature = temperature
        mock_flag = get_env("SPARKTECH_MOCK", default="")
        self._force_mock = force_mock if force_mock is not None else mock_flag in ("1", "true", "yes")
        self._client: Any | None = None
        self._call_count = 0

    @property
    def is_mock_mode(self) -> bool:
        return self._force_mock or not self._api_key.strip()

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def call_count(self) -> int:
        return self._call_count

    def _get_openai_client(self) -> Any:
        if OpenAI is None:
            raise LLMClientError(
                "未安装 openai 包，请执行 pip install -r requirements.txt"
            )
        if self._client is None:
            self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        return self._client

    def chat(self, messages: list[dict]) -> ChatCompletionResult:
        """根据完整 messages 历史生成 assistant 回复。"""
        if not messages:
            raise ValueError("messages 不能为空")

        self._call_count += 1
        if self.is_mock_mode:
            return self._mock_chat(messages)

        try:
            return self._real_chat(messages)
        except ConfigError:
            raise
        except APIError as exc:
            raise LLMClientError(f"OpenAI API 错误: {exc}") from exc
        except Exception as exc:
            raise LLMClientError(f"LLM 调用失败: {exc}") from exc

    def _mock_chat(self, messages: list[dict]) -> ChatCompletionResult:
        start = time.perf_counter()
        last_user = ""
        for item in reversed(messages):
            if item.get("role") == "user":
                last_user = str(item.get("content", ""))
                break

        digest = hashlib.md5(last_user.encode()).hexdigest()[:8]
        history_len = len(messages)
        reply = (
            f"[mock/{self._model}] 已收到你的第 {self._call_count} 轮提问："
            f"「{_preview_text(last_user)}」。"
            f"当前上下文共 {history_len} 条消息。（mock_id={digest}）"
        )
        latency_ms = (time.perf_counter() - start) * 1000
        return ChatCompletionResult(
            text=reply,
            model=self._model,
            vendor="openai",
            mock=True,
            prompt_tokens=max(1, sum(len(str(m.get("content", ""))) for m in messages) // 4),
            completion_tokens=max(1, len(reply) // 4),
            latency_ms=round(latency_ms, 2),
        )

    def _real_chat(self, messages: list[dict]) -> ChatCompletionResult:
        start = time.perf_counter()
        client = self._get_openai_client()
        response = client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        choice = response.choices[0].message
        usage = getattr(response, "usage", None)
        return ChatCompletionResult(
            text=choice.content or "",
            model=self._model,
            vendor="openai",
            mock=False,
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
            latency_ms=round(latency_ms, 2),
        )

    def describe(self) -> str:
        mode = "mock" if self.is_mock_mode else "live"
        return f"LLMClient(model={self._model}, mode={mode}, calls={self._call_count})"


def _preview_text(text: str, max_len: int = 40) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"
