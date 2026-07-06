# -*- coding: utf-8 -*-
"""
Day 19 · 支持 Function Calling 的 LLM 客户端

- OpenAI 兼容 chat/completions + tools
- 无 API Key 时 mock 模式：启发式解析用户意图并返回 tool_calls
- 绝不硬编码密钥
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
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
class AssistantMessage:
    """模型 assistant 消息，可能含 tool_calls。"""

    content: str | None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


@dataclass
class ChatCompletionResult:
    """chat_with_tools 的结构化返回。"""

    message: AssistantMessage
    model: str
    mode: str  # "live" | "mock"
    finish_reason: str = "stop"
    latency_ms: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


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


class ToolCallingLLMClient:
    """支持 tools / tool_choice 的轻量客户端。"""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
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

    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        *,
        tool_choice: str | dict[str, Any] = "auto",
        temperature: float = 0.2,
    ) -> ChatCompletionResult:
        """调用 chat/completions，可附带 tools schema。"""
        if not messages:
            raise ValueError("messages 不能为空")

        if self.is_mock_mode:
            return self._mock_chat_with_tools(messages, tools or [], temperature=temperature)
        return self._live_chat_with_tools(
            messages,
            tools or [],
            tool_choice=tool_choice,
            temperature=temperature,
        )

    def _mock_chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        *,
        temperature: float,
    ) -> ChatCompletionResult:
        """启发式 mock：根据用户文本决定返回 tool_calls 或最终文本。"""
        start = time.perf_counter()
        user_text = self._last_user_text(messages)
        tool_names = {t["function"]["name"] for t in tools if "function" in t}

        # 若上一条是 tool 结果，生成最终自然语言回复
        if messages and messages[-1].get("role") == "tool":
            reply = self._mock_finalize_from_tools(messages)
            latency_ms = (time.perf_counter() - start) * 1000
            return ChatCompletionResult(
                message=AssistantMessage(content=reply, tool_calls=[]),
                model=self._model,
                mode="mock",
                finish_reason="stop",
                latency_ms=round(latency_ms, 2),
                raw={"mock": True, "stage": "finalize"},
            )

        tool_calls = self._mock_plan_tool_calls(user_text, tool_names)
        if tool_calls:
            latency_ms = (time.perf_counter() - start) * 1000
            return ChatCompletionResult(
                message=AssistantMessage(content=None, tool_calls=tool_calls),
                model=self._model,
                mode="mock",
                finish_reason="tool_calls",
                latency_ms=round(latency_ms, 2),
                raw={"mock": True, "stage": "tool_calls"},
            )

        digest = hashlib.md5(user_text.encode()).hexdigest()[:6]
        reply = f"[mock] 无需工具即可回答：{user_text[:40]}（id={digest}）"
        latency_ms = (time.perf_counter() - start) * 1000
        return ChatCompletionResult(
            message=AssistantMessage(content=reply, tool_calls=[]),
            model=self._model,
            mode="mock",
            finish_reason="stop",
            latency_ms=round(latency_ms, 2),
            raw={"mock": True, "stage": "direct"},
        )

    def _mock_plan_tool_calls(
        self,
        user_text: str,
        available: set[str],
    ) -> list[dict[str, Any]]:
        """从用户文本推断应调用的工具（教学用启发式）。"""
        text = user_text.lower()
        calls: list[dict[str, Any]] = []

        # 天气
        if "get_weather" in available:
            city_match = re.search(
                r"(北京|上海|深圳|杭州|成都|[\u4e00-\u9fff]{2,4})",
                user_text,
            )
            if any(k in user_text for k in ("天气", "气温", "温度", "下雨", "weather")):
                city = city_match.group(1) if city_match else "北京"
                calls.append(self._make_tool_call("get_weather", {"city": city}))

        # 计算
        if "calculate" in available:
            expr_match = re.search(
                r"(\d[\d\s+\-*/().]*\d|\d+\s*[\+\-\*/]\s*\d+)",
                user_text,
            )
            if any(k in user_text for k in ("计算", "等于", "多少", "+", "*", "**")) or expr_match:
                expr = expr_match.group(1).strip() if expr_match else "1+1"
                expr = expr.replace("×", "*").replace("÷", "/")
                calls.append(self._make_tool_call("calculate", {"expression": expr}))

        # 产品库
        if "query_products" in available:
            if any(k in user_text for k in ("产品", "查询", "工单", "embedding", "硬件", "软件")):
                kw_match = re.search(r"查(?:询)?[「『\"']?(.*?)[」』\"']?(?:产品|信息)", user_text)
                keyword = kw_match.group(1) if kw_match else "工单"
                if not keyword.strip():
                    keyword = "星火"
                calls.append(
                    self._make_tool_call("query_products", {"keyword": keyword.strip(), "limit": 3})
                )

        return calls

    def _mock_finalize_from_tools(self, messages: list[dict[str, Any]]) -> str:
        """根据 tool 消息拼出最终 mock 回复。"""
        parts: list[str] = []
        for msg in messages:
            if msg.get("role") != "tool":
                continue
            name = msg.get("name", "tool")
            try:
                data = json.loads(msg.get("content", "{}"))
            except json.JSONDecodeError:
                data = {"raw": msg.get("content")}
            if name == "get_weather":
                parts.append(
                    f"{data.get('city', '该地')}当前{data.get('condition')}，"
                    f"气温 {data.get('temperature')}{data.get('unit', '°C')}，"
                    f"湿度 {data.get('humidity_percent')}%"
                )
            elif name == "calculate":
                parts.append(f"计算结果：{data.get('expression')} = {data.get('result')}")
            elif name == "query_products":
                names = [p["name"] for p in data.get("products", [])]
                parts.append(f"找到 {data.get('count', 0)} 个产品：" + "、".join(names[:3]))
            else:
                parts.append(f"{name} 返回：{json.dumps(data, ensure_ascii=False)[:80]}")
        return "；".join(parts) if parts else "[mock] 工具执行完成。"

    @staticmethod
    def _make_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": f"call_{uuid.uuid4().hex[:12]}",
            "type": "function",
            "function": {
                "name": name,
                "arguments": json.dumps(arguments, ensure_ascii=False),
            },
        }

    @staticmethod
    def _last_user_text(messages: list[dict[str, Any]]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                return content if isinstance(content, str) else str(content)
        return ""

    def _live_chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        *,
        tool_choice: str | dict[str, Any],
        temperature: float,
    ) -> ChatCompletionResult:
        if requests is None:
            raise LLMClientError("未安装 requests")

        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        start = time.perf_counter()
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self._timeout)
        except requests.RequestException as exc:
            raise LLMHTTPError(f"网络请求失败: {exc}") from exc

        latency_ms = (time.perf_counter() - start) * 1000
        if resp.status_code >= 400:
            raise LLMHTTPError(
                f"HTTP {resp.status_code}: {resp.text[:300]}",
                status_code=resp.status_code,
            )

        data = resp.json()
        choice = data["choices"][0]
        msg = choice["message"]
        tool_calls = msg.get("tool_calls") or []

        return ChatCompletionResult(
            message=AssistantMessage(
                content=msg.get("content"),
                tool_calls=tool_calls,
            ),
            model=data.get("model", self._model),
            mode="live",
            finish_reason=choice.get("finish_reason", "stop"),
            latency_ms=round(latency_ms, 2),
            raw=data,
        )


def main() -> None:
    print("=" * 60)
    print("Day 19 · ToolCallingLLMClient（mock 演示）")
    print("=" * 60)

    from schemas import load_all_schemas

    client = ToolCallingLLMClient()
    tools = load_all_schemas()
    print(f"模式: {client.mode} | 模型: {client.model}")

    messages = [{"role": "user", "content": "北京今天天气怎么样？"}]
    result = client.chat_with_tools(messages, tools)
    print(f"finish_reason: {result.finish_reason}")
    if result.message.has_tool_calls:
        print(json.dumps(result.message.tool_calls, ensure_ascii=False, indent=2))
    else:
        print(result.message.content)

    print("\n✅ llm_client.py 完成")


if __name__ == "__main__":
    main()
