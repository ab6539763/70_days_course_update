# -*- coding: utf-8 -*-
"""
Day 17 · Prompt 工程实验用 LLM 客户端

无 API Key 时进入 mock 模式，根据 Prompt 关键词返回确定性演示结果，
便于课堂与 CI 在无网络环境下验收翻译/摘要/改写/分类等任务。

运行：cd day17/code && python3 llm_client.py
"""

from __future__ import annotations

import hashlib
import json
import os
import re
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
    text: str
    model: str
    mode: str
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
    pass


class LLMHTTPError(LLMClientError):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


def load_dotenv_file(env_path: Path | None = None) -> None:
    if load_dotenv is None:
        return
    if env_path is not None:
        load_dotenv(env_path)
        return
    code_dir = Path(__file__).resolve().parent
    for candidate in (code_dir / ".env", code_dir.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()


def resolve_api_key(explicit_key: str | None = None) -> str:
    load_dotenv_file()
    if explicit_key:
        return explicit_key.strip()
    return (os.getenv(ENV_API_KEY) or "").strip()


def _extract_user_text(messages: list[dict[str, str]]) -> str:
    return next(
        (m["content"] for m in reversed(messages) if m.get("role") == "user"),
        "",
    )


def _extract_delimited_block(text: str, tag: str) -> str:
    pattern = rf"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _mock_task_response(user_text: str) -> str:
    """根据 Prompt 关键词返回教学用确定性结果。"""
    lower = user_text.lower()
    input_block = (
        _extract_delimited_block(user_text, "input")
        or _extract_delimited_block(user_text, "待处理文本")
        or _extract_delimited_block(user_text, "用户消息")
    )
    source = input_block or user_text

    if any(k in lower for k in ("翻译", "translate", "translation")):
        if re.search(r"[\u4e00-\u9fff]", source):
            return f"[mock 翻译] SparkTech intelligent customer service platform."
        return "[mock 翻译] 星火科技智能客服平台。"

    if any(k in lower for k in ("摘要", "总结", "summary", "summarize")):
        snippet = source[:80].replace("\n", " ")
        return f"[mock 摘要] 核心要点：{snippet}…（已压缩为一句话）"

    if any(k in lower for k in ("改写", "rewrite", "润色", "重写")):
        return f"[mock 改写] 尊敬的用户，{source.strip()[:60]}。感谢您的理解与支持。"

    if any(k in lower for k in ("分类", "classify", "意图", "intent")):
        if any(w in source for w in ("退款", "退货", "投诉")):
            label = "投诉/退款"
        elif any(w in source for w in ("怎么", "如何", "咨询", "?")):
            label = "产品咨询"
        elif any(w in source for w in ("谢谢", "感谢")):
            label = "感谢/寒暄"
        else:
            label = "其他"
        if "json" in lower or "{" in user_text:
            return json.dumps(
                {"intent": label, "confidence": 0.87, "language": "zh"},
                ensure_ascii=False,
            )
        return f"[mock 分类] {label}"

    if "json" in lower and "{" in user_text:
        return json.dumps(
            {"result": "ok", "preview": source[:40]},
            ensure_ascii=False,
        )

    digest = hashlib.md5(user_text.encode()).hexdigest()[:8]
    return (
        f"[mock/{DEFAULT_MODEL}] 已处理 Prompt（id={digest}）："
        f"{source[:50]}{'…' if len(source) > 50 else ''}"
    )


class LLMClient:
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
        if not messages:
            raise ValueError("messages 不能为空")
        if self.is_mock_mode:
            return self._mock_chat(messages, **kwargs)
        return self._live_chat(messages, **kwargs)

    def _mock_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> ChatResponse:
        start = time.perf_counter()
        user_text = _extract_user_text(messages)
        reply = _mock_task_response(user_text)
        latency_ms = (time.perf_counter() - start) * 1000
        return ChatResponse(
            text=reply,
            model=self._model,
            mode="mock",
            latency_ms=round(latency_ms, 2),
            prompt_tokens=max(1, len(user_text) // 4),
            completion_tokens=max(1, len(reply) // 4),
            raw={"mock": True},
        )

    def _live_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> ChatResponse:
        if requests is None:
            raise LLMClientError("未安装 requests，请 pip install requests")

        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": kwargs.get("model", self._model),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.3),
        }
        if kwargs.get("response_format"):
            payload["response_format"] = kwargs["response_format"]

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
        text = data["choices"][0]["message"]["content"]
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
    print("Day 17 · llm_client.py（mock 模式）")
    print("=" * 60)
    client = LLMClient()
    print(f"模式: {client.mode} | 模型: {client.model}")
    messages = [{"role": "user", "content": "请将以下文本翻译为英文：<input>星火智服</input>"}]
    result = client.chat(messages)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
