# -*- coding: utf-8 -*-
"""
Day 12 · 星火智服 LLM HTTP 客户端（基线版）

业务背景：Day 12 首次用 requests 调 OpenAI 兼容接口。
本模块提供最小可用客户端；Day 13 在其上叠加 retry / timeout 装饰器。

特性：
- python-dotenv 加载 OPENAI_API_KEY
- 无 Key 时自动进入 mock 模式（培训环境友好）
- 统一 chat(messages) 接口，返回结构化 dict

运行：cd day13/code && python3 llm_client.py
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
ENV_API_KEY = "OPENAI_API_KEY"
ENV_BASE_URL = "OPENAI_BASE_URL"
ENV_MODEL = "OPENAI_MODEL"


@dataclass
class ChatResponse:
    """chat() 的结构化返回，便于日志与测试断言。"""

    text: str
    model: str
    mode: str  # "live" | "mock"
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "model": self.model,
            "mode": self.mode,
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
        }


class LLMClientError(RuntimeError):
    """LLM 客户端业务错误基类。"""


class LLMHTTPError(LLMClientError):
    """HTTP 层错误（状态码非 2xx 或网络异常）。"""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class LLMConfigError(LLMClientError):
    """配置缺失或非法。"""


def load_dotenv_file(env_path: Path | None = None) -> None:
    """加载 .env；未安装 python-dotenv 时静默跳过。"""
    if load_dotenv is None:
        return
    if env_path is not None:
        load_dotenv(env_path)
        return
    # 默认从 code/ 目录向上查找 .env
    code_dir = Path(__file__).resolve().parent
    for candidate in (code_dir / ".env", code_dir.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()


def resolve_api_key(explicit_key: str | None = None) -> str:
    """解析 API Key：显式参数 > 环境变量 > 空（触发 mock）。"""
    load_dotenv_file()
    if explicit_key:
        return explicit_key.strip()
    return (os.getenv(ENV_API_KEY) or "").strip()


class LLMClient:
    """
    Day 12 基线 LLM 客户端。

    调用方只需关心 chat(messages)；内部根据是否配置 Key 选择 live / mock。
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        load_dotenv_file()
        self._api_key = resolve_api_key(api_key)
        self._base_url = (base_url or os.getenv(ENV_BASE_URL) or DEFAULT_BASE_URL).rstrip("/")
        self._model = model or os.getenv(ENV_MODEL) or DEFAULT_MODEL
        self._timeout = timeout

    @property
    def model(self) -> str:
        return self._model

    @property
    def is_mock_mode(self) -> bool:
        return not self._api_key

    @property
    def mode(self) -> str:
        return "mock" if self.is_mock_mode else "live"

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> ChatResponse:
        """
        OpenAI 兼容 chat/completions 调用。

        Args:
            messages: [{"role": "user", "content": "..."}]
        """
        if not messages:
            raise ValueError("messages 不能为空")

        if self.is_mock_mode:
            return self._mock_chat(messages, **kwargs)
        return self._live_chat(messages, **kwargs)

    def _mock_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> ChatResponse:
        """无 Key 时的确定性 mock，便于 CI 与课堂演示。"""
        start = time.perf_counter()
        user_text = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "",
        )
        digest = hashlib.md5(user_text.encode()).hexdigest()[:8]
        reply = (
            f"[mock/{self._model}] 已收到：{user_text[:60]}"
            f"{'…' if len(user_text) > 60 else ''}（id={digest}）"
        )
        latency_ms = (time.perf_counter() - start) * 1000
        return ChatResponse(
            text=reply,
            model=self._model,
            mode="mock",
            latency_ms=round(latency_ms, 2),
            prompt_tokens=max(1, len(user_text) // 4),
            completion_tokens=max(1, len(reply) // 4),
            raw={"mock": True, "digest": digest},
        )

    def _live_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> ChatResponse:
        """真实 HTTP 调用（Day 12 基线，无 retry/timeout 装饰）。"""
        if requests is None:
            raise LLMConfigError("未安装 requests，请 pip install requests")

        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": kwargs.get("model", self._model),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        start = time.perf_counter()
        try:
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=kwargs.get("timeout", self._timeout),
            )
        except requests.RequestException as exc:
            raise LLMHTTPError(f"网络请求失败: {exc}") from exc

        latency_ms = (time.perf_counter() - start) * 1000

        if resp.status_code >= 400:
            raise LLMHTTPError(
                f"HTTP {resp.status_code}: {resp.text[:200]}",
                status_code=resp.status_code,
            )

        data = resp.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMHTTPError(f"响应格式异常: {data!r}") from exc

        usage = data.get("usage") or {}
        return ChatResponse(
            text=text,
            model=data.get("model", self._model),
            mode="live",
            latency_ms=round(latency_ms, 2),
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            raw=data,
        )


def main() -> None:
    print("=" * 60)
    print("Day 12 基线 · llm_client.py（mock 模式演示）")
    print("=" * 60)

    client = LLMClient()
    print(f"模式: {client.mode} | 模型: {client.model}")

    messages = [{"role": "user", "content": "用一句话介绍星火智服工单系统。"}]
    result = client.chat(messages)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    print("\n✅ llm_client.py 完成")


if __name__ == "__main__":
    main()
