# -*- coding: utf-8 -*-
"""
Day 18 · 高级 Prompt 实验用 LLM 客户端

mock 模式支持：CoT 推理链、意图分类 JSON、注入防御演示、JSON Mode 模拟。

运行：cd day18/code && python3 llm_client.py
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

INTENT_LABELS = (
    "产品咨询",
    "订单物流",
    "投诉退款",
    "账户问题",
    "技术支持",
    "感谢寒暄",
    "其他",
)


@dataclass
class ChatResponse:
    text: str
    model: str
    mode: str
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "model": self.model,
            "mode": self.mode,
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "tool_calls": self.tool_calls,
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


def _all_message_text(messages: list[dict[str, str]]) -> str:
    return "\n".join(m.get("content", "") for m in messages)


def _extract_user_message(messages: list[dict[str, str]]) -> str:
    return next(
        (m["content"] for m in reversed(messages) if m.get("role") == "user"),
        "",
    )


def _extract_delimited(text: str, tag: str) -> str:
    m = re.search(rf"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _classify_intent(text: str) -> tuple[str, float, list[str]]:
    """规则 mock：模拟智能客服意图分类。"""
    rules: list[tuple[str, list[str], float]] = [
        ("投诉退款", ["退款", "退货", "投诉", "差评", "赔偿"], 0.92),
        ("订单物流", ["物流", "快递", "发货", "到哪了", "订单号"], 0.90),
        ("账户问题", ["登录", "密码", "账号", "注册", "验证码"], 0.88),
        ("技术支持", ["API", "401", "403", "报错", "接口", "部署"], 0.91),
        ("产品咨询", ["怎么", "如何", "多少钱", "功能", "支持吗", "?"], 0.85),
        ("感谢寒暄", ["谢谢", "感谢", "辛苦了", "你好"], 0.80),
    ]
    for label, keywords, conf in rules:
        if any(k.lower() in text.lower() for k in keywords):
            slots = [k for k in keywords if k.lower() in text.lower()][:3]
            return label, conf, slots
    return "其他", 0.55, []


def _mock_cot_response(problem: str) -> str:
    return (
        "思考过程：\n"
        "1. 识别已知条件与求解目标。\n"
        "2. 列出中间步骤，逐步推导。\n"
        "3. 核对边界情况。\n"
        f"最终答案：[mock CoT] 针对「{problem[:30]}…」的推导结论为 42（演示用）。"
    )


def _mock_intent_json(user_msg: str) -> str:
    intent, confidence, slots = _classify_intent(user_msg)
    payload = {
        "intent": intent,
        "confidence": round(confidence, 2),
        "slots": {s: "detected" for s in slots} if slots else {},
        "need_human": intent in ("投诉退款", "账户问题") and confidence > 0.85,
        "suggested_reply": f"已识别为【{intent}】，mock 模式自动生成话术骨架。",
    }
    return json.dumps(payload, ensure_ascii=False)


def _mock_injection_defense(user_text: str) -> str:
    lower = user_text.lower()
    injection_signals = [
        "ignore previous",
        "忽略以上",
        "忽略之前",
        "system:",
        "你现在是黑客",
        "jailbreak",
        "dAN",
    ]
    if any(sig in lower for sig in injection_signals):
        return json.dumps(
            {
                "blocked": True,
                "reason": "检测到疑似 Prompt 注入，已拒绝执行越权指令。",
                "safe_response": "我只能在客服范围内协助您，请描述具体业务问题。",
            },
            ensure_ascii=False,
        )
    safe_input = _extract_delimited(user_text, "user_input") or user_text
    return json.dumps(
        {
            "blocked": False,
            "parsed_input": safe_input[:200],
            "safe_response": f"收到您的问题：{safe_input[:60]}…",
        },
        ensure_ascii=False,
    )


def _mock_structured_json(user_text: str, response_format: dict[str, Any] | None) -> str:
    if response_format and response_format.get("type") == "json_object":
        if "intent" in user_text.lower() or "分类" in user_text:
            msg = _extract_delimited(user_text, "user_message") or user_text
            return _mock_intent_json(msg)
        return json.dumps({"status": "ok", "mock": True}, ensure_ascii=False)
    return _mock_intent_json(_extract_user_message([{"role": "user", "content": user_text}]))


def _mock_tool_call(user_text: str, tools: list[dict[str, Any]] | None) -> ChatResponse:
    """模拟 Function Calling：查询订单。"""
    order_id_match = re.search(r"ORD[-_]?\d+", user_text, flags=re.IGNORECASE)
    order_id = order_id_match.group(0) if order_id_match else "ORD-0000"
    tool_call = {
        "id": "call_mock_001",
        "type": "function",
        "function": {
            "name": "query_order_status",
            "arguments": json.dumps({"order_id": order_id}, ensure_ascii=False),
        },
    }
    result = {
        "order_id": order_id,
        "status": "已发货",
        "carrier": "顺丰",
        "eta": "2026-07-08",
    }
    text = json.dumps(
        {
            "tool_used": "query_order_status",
            "tool_result": result,
            "assistant_reply": f"您的订单 {order_id} 已发货，预计 7 月 8 日送达。",
        },
        ensure_ascii=False,
    )
    return ChatResponse(
        text=text,
        model=DEFAULT_MODEL,
        mode="mock",
        tool_calls=[tool_call],
        raw={"mock": True, "function_call": True},
    )


def _mock_task_response(
    messages: list[dict[str, str]],
    *,
    response_format: dict[str, Any] | None = None,
    tools: list[dict[str, Any]] | None = None,
) -> ChatResponse:
    full = _all_message_text(messages)
    user_text = _extract_user_message(messages)

    if tools:
        return _mock_tool_call(user_text, tools)

    lower = full.lower()
    if "逐步思考" in full or "chain of thought" in lower or "cot" in lower:
        problem = _extract_delimited(user_text, "problem") or user_text
        reply = _mock_cot_response(problem)
    elif "注入" in full or "injection" in lower or "jailbreak" in lower:
        reply = _mock_injection_defense(user_text)
    elif "intent" in lower or "意图分类" in full or "客服" in full:
        msg = _extract_delimited(user_text, "user_message") or user_text
        reply = _mock_intent_json(msg)
    elif response_format:
        reply = _mock_structured_json(user_text, response_format)
    else:
        digest = hashlib.md5(user_text.encode()).hexdigest()[:8]
        reply = f"[mock] 已处理（id={digest}）"

    return ChatResponse(
        text=reply,
        model=DEFAULT_MODEL,
        mode="mock",
        raw={"mock": True},
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

        start = time.perf_counter()
        if self.is_mock_mode:
            resp = _mock_task_response(
                messages,
                response_format=kwargs.get("response_format"),
                tools=kwargs.get("tools"),
            )
            resp.model = self._model
            resp.latency_ms = round((time.perf_counter() - start) * 1000, 2)
            resp.prompt_tokens = max(1, len(_all_message_text(messages)) // 4)
            resp.completion_tokens = max(1, len(resp.text) // 4)
            return resp

        return self._live_chat(messages, **kwargs)

    def _live_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> ChatResponse:
        if requests is None:
            raise LLMClientError("未安装 requests")

        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": kwargs.get("model", self._model),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.2),
        }
        if kwargs.get("response_format"):
            payload["response_format"] = kwargs["response_format"]
        if kwargs.get("tools"):
            payload["tools"] = kwargs["tools"]
            payload["tool_choice"] = kwargs.get("tool_choice", "auto")

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
        message = data["choices"][0]["message"]
        usage = data.get("usage") or {}
        return ChatResponse(
            text=message.get("content") or "",
            model=data.get("model", self._model),
            mode="live",
            latency_ms=round(latency_ms, 2),
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            raw=data,
            tool_calls=message.get("tool_calls") or [],
        )


def main() -> None:
    client = LLMClient()
    print(f"Day 18 llm_client · mode={client.mode}")
    r = client.chat(
        [{"role": "user", "content": "对用户消息做意图分类 <user_message>我要退款</user_message>"}],
        response_format={"type": "json_object"},
    )
    print(r.text)


if __name__ == "__main__":
    main()
