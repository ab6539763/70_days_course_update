# -*- coding: utf-8 -*-
"""
Day 16 · 参数化 LLM 客户端（衔接 Day 12–14）

在 Day 13 ResilientLLMClient / Day 12 LLMClient 之上扩展：
- chat(messages, temperature=..., top_p=..., max_tokens=..., frequency_penalty=...)
- chat_stream(messages, ...) → 生成器逐 chunk 产出
- mock 模式：无 Key 时确定性回复 + 模拟流式打字

运行：cd day16/code && python3 llm_compat.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator, Iterator

WORKSPACE = Path(__file__).resolve().parents[2]
DAY12_CODE = WORKSPACE / "day12" / "code"
DAY13_CODE = WORKSPACE / "day13" / "code"
DAY14_LLM = WORKSPACE / "day14" / "project1" / "llm_client.py"
DATA_DIR = Path(__file__).resolve().parent / "data"

CLIENT_SOURCE = "builtin-fallback"

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore[assignment]

try:
    import requests
except ImportError:
    requests = None  # type: ignore[assignment]

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
STREAM_MOCK_DELAY = float(os.getenv("STREAM_MOCK_DELAY", "0.03"))


@dataclass
class StreamResult:
    """流式调用结束后的汇总信息。"""

    full_text: str
    model: str
    mode: str
    completion_tokens: int = 0
    latency_ms: float = 0.0


@dataclass
class ParametricChatResponse:
    """统一 chat 返回，兼容 Day 12/13 ChatResponse 字段。"""

    text: str
    model: str
    mode: str
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    params: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "model": self.model,
            "mode": self.mode,
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "params": self.params,
        }


def _load_env() -> None:
    if load_dotenv is None:
        return
    code_dir = Path(__file__).resolve().parent
    for p in (code_dir / ".env", code_dir.parent / ".env"):
        if p.is_file():
            load_dotenv(p)
            return
    load_dotenv()


def load_demo_defaults() -> dict[str, Any]:
    """读取 param_presets.json 中的 demo_defaults。"""
    path = DATA_DIR / "param_presets.json"
    if not path.is_file():
        return {
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": 512,
            "frequency_penalty": 0.3,
            "stream": True,
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    return dict(data.get("demo_defaults", {}))


def merge_params(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """合并默认演示参数与调用方覆盖项。"""
    base = load_demo_defaults()
    # 只保留 API 相关键
    keys = ("temperature", "top_p", "max_tokens", "frequency_penalty", "presence_penalty", "stop")
    merged = {k: base[k] for k in keys if k in base}
    if overrides:
        for k, v in overrides.items():
            if k in keys or k == "model":
                merged[k] = v
    return merged


def _ensure_path(path: Path) -> None:
    s = str(path)
    if path.is_dir() and s not in sys.path:
        sys.path.insert(0, s)


def _import_base_client() -> Any | None:
    """尝试导入 Day 13 / Day 12 基线客户端类。"""
    global CLIENT_SOURCE
    if DAY13_CODE.is_dir():
        _ensure_path(DAY13_CODE)
        try:
            from resilient_llm_client import ResilientLLMClient

            CLIENT_SOURCE = "day13/resilient_llm_client.py"
            return ResilientLLMClient
        except ImportError:
            try:
                from llm_client import LLMClient

                CLIENT_SOURCE = "day13/llm_client.py"
                return LLMClient
            except ImportError:
                pass
    if DAY12_CODE.is_dir():
        _ensure_path(DAY12_CODE)
        try:
            from llm_client import LLMClient

            CLIENT_SOURCE = "day12/llm_client.py"
            return LLMClient
        except ImportError:
            pass
    CLIENT_SOURCE = "day16/llm_compat.py (standalone)"
    return None


class ParametricLLMClient:
    """
    参数化 LLM 客户端：组合 Day 12/13 非流式 chat + 本模块流式与参数合并。

    无 API Key 时进入 mock 模式。
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        _load_env()
        self._api_key = (api_key or os.getenv("OPENAI_API_KEY", "")).strip()
        mock_flag = os.getenv("SPARKTECH_MOCK", "").lower()
        self._force_mock = mock_flag in ("1", "true", "yes")
        self._base_url = (base_url or os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self._timeout = timeout

        base_cls = _import_base_client()
        self._base_client: Any | None = None
        if base_cls is not None:
            try:
                self._base_client = base_cls(
                    api_key=self._api_key or None,
                    base_url=self._base_url,
                    model=self._model,
                    timeout=timeout,
                )
                if hasattr(self._base_client, "model"):
                    self._model = self._base_client.model
            except TypeError:
                self._base_client = base_cls(api_key=self._api_key or None)

    @property
    def mode(self) -> str:
        if self._force_mock or not self._api_key:
            return "mock"
        return "live"

    @property
    def model(self) -> str:
        return self._model

    @property
    def client_source(self) -> str:
        return CLIENT_SOURCE

    def _mock_reply(self, messages: list[dict[str, str]], params: dict[str, Any]) -> str:
        """根据参数生成略有差异的 mock 回复，便于对比实验。"""
        user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "",
        )
        system = next(
            (m["content"] for m in messages if m.get("role") == "system"),
            "",
        )
        temp = float(params.get("temperature", 0.7))
        freq = float(params.get("frequency_penalty", 0))
        digest = hashlib.md5((user + str(temp)).encode()).hexdigest()[:6]

        tone = "简洁专业" if temp < 0.4 else ("平衡" if temp < 0.8 else "活泼发散")
        greeting = "您好！您好！" if freq < 0.2 else "您好，"
        sys_hint = "（已加载人设）" if system else "（无人设）"

        body = (
            f"{greeting}关于「{user[:40]}{'…' if len(user) > 40 else ''}」——"
            f"这是 mock 回复，语气={tone}，temp={temp}，freq_pen={freq}。"
            f"{sys_hint} id={digest}"
        )
        max_tok = int(params.get("max_tokens", 512))
        # 粗略按字符截断模拟 max_tokens
        char_limit = max(40, max_tok // 2)
        return body[:char_limit]

    def chat(
        self, messages: list[dict[str, str]], **kwargs: Any
    ) -> ParametricChatResponse:
        """非流式对话，合并采样参数。"""
        if not messages:
            raise ValueError("messages 不能为空")

        params = merge_params(kwargs)
        start = time.perf_counter()

        # 优先委托 Day 12/13 基线客户端（仅非流式）
        if self._base_client is not None and self.mode == "live":
            try:
                resp = self._base_client.chat(messages, **params)
                latency = (time.perf_counter() - start) * 1000
                return ParametricChatResponse(
                    text=resp.text,
                    model=getattr(resp, "model", self._model),
                    mode=getattr(resp, "mode", "live"),
                    latency_ms=round(latency, 2),
                    prompt_tokens=getattr(resp, "prompt_tokens", 0),
                    completion_tokens=getattr(resp, "completion_tokens", 0),
                    params=params,
                    raw=getattr(resp, "raw", {}),
                )
            except Exception:
                pass  # 降级到本模块 live HTTP

        if self.mode == "live":
            return self._live_chat(messages, params, start)

        text = self._mock_reply(messages, params)
        latency = (time.perf_counter() - start) * 1000
        user_len = sum(len(m.get("content", "")) for m in messages)
        return ParametricChatResponse(
            text=text,
            model=self._model,
            mode="mock",
            latency_ms=round(latency, 2),
            prompt_tokens=max(1, user_len // 4),
            completion_tokens=max(1, len(text) // 4),
            params=params,
            raw={"mock": True},
        )

    def _live_chat(
        self,
        messages: list[dict[str, str]],
        params: dict[str, Any],
        start: float,
    ) -> ParametricChatResponse:
        """OpenAI 兼容 HTTP chat/completions（非流式）。"""
        if requests is None:
            raise RuntimeError("未安装 requests")

        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": params.get("model", self._model),
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 1.0),
            "max_tokens": params.get("max_tokens", 512),
        }
        if "frequency_penalty" in params:
            payload["frequency_penalty"] = params["frequency_penalty"]
        if "presence_penalty" in params:
            payload["presence_penalty"] = params["presence_penalty"]
        if params.get("stop"):
            payload["stop"] = params["stop"]

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=self._timeout)
        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")

        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage") or {}
        latency = (time.perf_counter() - start) * 1000
        return ParametricChatResponse(
            text=text,
            model=data.get("model", self._model),
            mode="live",
            latency_ms=round(latency, 2),
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            params=params,
            raw=data,
        )

    def chat_stream(
        self, messages: list[dict[str, str]], **kwargs: Any
    ) -> Iterator[str]:
        """
        流式生成文本片段。

        Yields:
            文本 chunk 字符串
        """
        params = merge_params(kwargs)
        if self.mode == "mock":
            text = self._mock_reply(messages, params)
            yield from self._mock_stream_chunks(text)
            return

        if requests is None:
            raise RuntimeError("未安装 requests")

        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": params.get("model", self._model),
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 1.0),
            "max_tokens": params.get("max_tokens", 512),
            "stream": True,
        }
        if "frequency_penalty" in params:
            payload["frequency_penalty"] = params["frequency_penalty"]

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        with requests.post(
            url, headers=headers, json=payload, timeout=self._timeout, stream=True
        ) as resp:
            if resp.status_code >= 400:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

    def _mock_stream_chunks(self, text: str, chunk_size: int = 3) -> Generator[str, None, None]:
        """mock 流式：按固定字数切分并 sleep。"""
        for i in range(0, len(text), chunk_size):
            yield text[i : i + chunk_size]
            if STREAM_MOCK_DELAY > 0:
                time.sleep(STREAM_MOCK_DELAY)

    def collect_stream(
        self, messages: list[dict[str, str]], **kwargs: Any
    ) -> StreamResult:
        """消费完整流式输出并汇总。"""
        start = time.perf_counter()
        parts: list[str] = []
        for chunk in self.chat_stream(messages, **kwargs):
            parts.append(chunk)
        full = "".join(parts)
        latency = (time.perf_counter() - start) * 1000
        return StreamResult(
            full_text=full,
            model=self._model,
            mode=self.mode,
            completion_tokens=max(1, len(full) // 4),
            latency_ms=round(latency, 2),
        )


def get_llm_client(**kwargs: Any) -> ParametricLLMClient:
    """工厂函数：获取参数化客户端。"""
    return ParametricLLMClient(**kwargs)


def get_day14_client_hint() -> str:
    if DAY14_LLM.is_file():
        return (
            f"Day 14 多轮助手: {DAY14_LLM}\n"
            "  可在 project1 中读取 demo_defaults.json 作为默认 temperature"
        )
    return "Day 14 project1/llm_client.py 未找到"


def main() -> None:
    print("=" * 60)
    print("Day 16 · llm_compat · ParametricLLMClient")
    print("=" * 60)
    client = get_llm_client()
    print(f"来源: {CLIENT_SOURCE}")
    print(f"模式: {client.mode} | 模型: {client.model}")
    print(get_day14_client_hint())
    print()

    messages = [
        {"role": "system", "content": "你是星火智服客服，回答简洁。"},
        {"role": "user", "content": "演示参数化客户端。"},
    ]
    resp = client.chat(messages, temperature=0.3)
    print("非流式:", json.dumps(resp.to_dict(), ensure_ascii=False, indent=2))
    print("\n流式:", end=" ")
    for c in client.chat_stream(messages, temperature=0.3):
        print(c, end="", flush=True)
    print("\n\n✅ llm_compat.py 完成")


if __name__ == "__main__":
    main()
