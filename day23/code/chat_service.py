# -*- coding: utf-8 -*-
"""Day 23 · Chat 业务层：会话管理、工具 mock、可选 live LLM。"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[misc, assignment]

from models import ChatRequest, ChatResponse, Message

CODE_DIR = __import__("pathlib").Path(__file__).resolve().parent
DEFAULT_MAX_MESSAGES = 20

SYSTEM_PROMPT = """你是星火智服（SparkTech）智能客服助手。
回答简洁友好，使用中文。若已调用工具，请基于工具结果组织自然语言回复。"""

_MOCK_ORDERS: dict[str, dict[str, str]] = {
    "ST-10086": {
        "status": "已发货",
        "eta": "2026-07-08",
        "carrier": "顺丰",
    },
    "ST-20001": {
        "status": "处理中",
        "eta": "待定",
        "carrier": "-",
    },
}


def _load_env() -> None:
    if load_dotenv is None:
        return
    for path in (CODE_DIR / ".env", CODE_DIR.parent / ".env"):
        if path.is_file():
            load_dotenv(path)
            return
    load_dotenv()


def get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[[dict[str, Any]], str]
    keywords: tuple[str, ...] = field(default_factory=tuple)


def _extract_city(text: str) -> str:
    for marker in ("天气", "气温", "温度"):
        if marker in text:
            idx = text.index(marker)
            prefix = text[:idx].strip()
            city = re.sub(r"[查的一下怎样如何\s]", "", prefix)
            city = city.strip() or "上海"
            return city[-6:] if len(city) > 6 else city
    return "上海"


def _extract_order_id(text: str) -> str:
    match = re.search(r"ST-?\d+", text, re.IGNORECASE)
    if match:
        raw = match.group(0).upper()
        return raw if raw.startswith("ST-") else f"ST-{raw[2:]}"
    return "ST-10086"


def _extract_expression(text: str) -> str:
    expr = re.sub(r"(计算|等于|请算|帮我算)", "", text).strip()
    return expr.replace("×", "*").replace("÷", "/") or "0"


def _handle_get_weather(args: dict[str, Any]) -> str:
    city = str(args.get("city", "上海"))
    seed = sum(ord(c) for c in city) % 5
    conditions = ["晴", "多云", "阴", "小雨", "晴转多云"]
    temp = 18 + seed * 3
    payload = {
        "city": city,
        "condition": conditions[seed],
        "temp_c": temp,
        "humidity_pct": 50 + seed * 5,
        "source": "mock_weather_api",
    }
    return json.dumps(payload, ensure_ascii=False)


def _handle_lookup_order(args: dict[str, Any]) -> str:
    order_id = str(args.get("order_id", "ST-10086")).upper()
    if not order_id.startswith("ST-"):
        order_id = f"ST-{order_id}"
    record = _MOCK_ORDERS.get(
        order_id,
        {"status": "未找到", "eta": "-", "carrier": "-"},
    )
    payload = {"order_id": order_id, **record}
    return json.dumps(payload, ensure_ascii=False)


def _handle_calc(args: dict[str, Any]) -> str:
    expr = str(args.get("expression", "0"))
    if not re.fullmatch(r"[\d\s+\-*/().]+", expr):
        return json.dumps({"error": "表达式含非法字符", "expression": expr})
    try:
        value = eval(expr, {"__builtins__": {}}, {})  # noqa: S307 教学 mock
        return json.dumps({"expression": expr, "result": value}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc), "expression": expr})


class ToolRegistry:
    """关键词路由 mock 工具，文案对齐 Day 21/22。"""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self._tools["get_weather"] = ToolSpec(
            name="get_weather",
            description="查询城市天气",
            parameters={},
            handler=_handle_get_weather,
            keywords=("天气", "气温", "温度", "下雨"),
        )
        self._tools["lookup_order"] = ToolSpec(
            name="lookup_order",
            description="查询订单物流",
            parameters={},
            handler=_handle_lookup_order,
            keywords=("订单", "物流", "ST-", "st-"),
        )
        self._tools["calc"] = ToolSpec(
            name="calc",
            description="数学计算",
            parameters={},
            handler=_handle_calc,
            keywords=("计算", "等于", "乘", "除", "加", "减"),
        )

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def maybe_invoke(self, user_text: str) -> ToolCall | None:
        text = user_text.strip()
        if not text:
            return None

        if re.search(r"ST-?\d+", text, re.IGNORECASE) or "订单" in text:
            return ToolCall(
                name="lookup_order",
                arguments={"order_id": _extract_order_id(text)},
            )

        if re.search(r"\d\s*[\+\-\*/]\s*\d", text) or any(
            kw in text for kw in ("计算", "等于", "乘", "除", "加", "减")
        ):
            return ToolCall(
                name="calc",
                arguments={"expression": _extract_expression(text)},
            )

        for name, spec in self._tools.items():
            if name in ("lookup_order", "calc"):
                continue
            if any(kw in text for kw in spec.keywords):
                if name == "get_weather":
                    return ToolCall(name=name, arguments={"city": _extract_city(text)})
                return ToolCall(name=name, arguments={})
        return None

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        spec = self._tools.get(name)
        if spec is None:
            return json.dumps({"error": f"未知工具: {name}"})
        return spec.handler(arguments)


class ConversationSession:
    """按 session_id 维护多轮 messages。"""

    def __init__(self, *, system_prompt: str = SYSTEM_PROMPT) -> None:
        self._messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def add_user_message(self, text: str) -> None:
        self._messages.append({"role": "user", "content": text})
        self._trim()

    def add_assistant_message(self, text: str) -> None:
        self._messages.append({"role": "assistant", "content": text})
        self._trim()

    def add_tool_result(self, tool_name: str, result: str) -> None:
        self._messages.append(
            {"role": "user", "content": f"[tool_result:{tool_name}] {result}"}
        )
        self._trim()

    def to_api_messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def _trim(self) -> None:
        non_system = [m for m in self._messages if m["role"] != "system"]
        if len(non_system) > DEFAULT_MAX_MESSAGES:
            system = [m for m in self._messages if m["role"] == "system"]
            self._messages = system + non_system[-DEFAULT_MAX_MESSAGES:]

    def to_message_models(self) -> list[Message]:
        return [
            Message(role=m["role"], content=m["content"])  # type: ignore[arg-type]
            for m in self._messages
            if m["role"] in ("system", "user", "assistant")
        ]


def _format_tool_reply(tool_name: str, raw_result: str) -> str:
    try:
        data = json.loads(raw_result)
    except json.JSONDecodeError:
        return f"已处理工具 {tool_name} 结果。"

    if tool_name == "get_weather":
        return (
            f"{data['city']}当前天气：{data['condition']}，"
            f"{data['temp_c']}°C，湿度 {data['humidity_pct']}%。"
            f"（数据来源：{data.get('source', 'mock_weather_api')}）"
        )
    if tool_name == "lookup_order":
        return (
            f"订单 {data['order_id']}：{data['status']}，"
            f"承运 {data.get('carrier', '-')}，"
            f"预计 {data.get('eta', '-')} 送达。"
        )
    if tool_name == "calc":
        if "error" in data:
            return f"计算失败：{data['error']}"
        return f"{data['expression']} = {data['result']}"
    return json.dumps(data, ensure_ascii=False)


def _pick_greeting_reply(text: str) -> str | None:
    lowered = text.lower()
    if any(kw in text for kw in ("你好", "您好")) or lowered in ("hello", "hi"):
        return "您好！很高兴为您服务，请问有什么可以帮您？"
    if "帮助" in text or "help" in lowered:
        return (
            "我可以帮您：\n"
            "1. 查询天气（例：上海天气）\n"
            "2. 查询订单（例：ST-10086）\n"
            "3. 日常问候"
        )
    return None


def _default_mock_reply(text: str) -> str:
    return (
        "已收到您的消息。请尝试包含「天气」「订单」或「你好」等关键词。"
        "（Day 23 mock 模式）"
    )


class ChatService:
    """封装会话存储与回复生成。"""

    def __init__(self) -> None:
        _load_env()
        self._sessions: dict[str, ConversationSession] = {}
        self._tools = ToolRegistry()
        mock_flag = get_env("SPARKTECH_MOCK", "1")
        self._force_mock = mock_flag in ("1", "true", "yes", "")
        self._api_key = get_env("OPENAI_API_KEY")
        self._model = get_env("OPENAI_MODEL", "gpt-4o-mini")
        self._base_url = get_env("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self._client: Any | None = None

    @property
    def is_mock_mode(self) -> bool:
        return self._force_mock or not self._api_key

    @property
    def mode_label(self) -> str:
        return "mock" if self.is_mock_mode else "live"

    def get_session(self, session_id: str) -> ConversationSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession()
        return self._sessions[session_id]

    def clear_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._sessions[session_id].clear()

    def chat(self, request: ChatRequest) -> ChatResponse:
        if request.stream:
            # Day 23 仅教学非流式；流式端点留 Day 24+
            pass

        session = self.get_session(request.session_id)
        user_text = request.message
        session.add_user_message(user_text)

        tools_used: list[str] = []
        tool_call = self._tools.maybe_invoke(user_text)
        if tool_call:
            tools_used.append(tool_call.name)
            raw = self._tools.execute(tool_call.name, tool_call.arguments)
            session.add_tool_result(tool_call.name, raw)
            reply = _format_tool_reply(tool_call.name, raw)
        else:
            greeting = _pick_greeting_reply(user_text)
            if greeting:
                reply = greeting
            elif self.is_mock_mode:
                reply = _default_mock_reply(user_text)
            else:
                reply = self._live_chat(session.to_api_messages())

        session.add_assistant_message(reply)
        return ChatResponse(
            reply=reply,
            session_id=request.session_id,
            tools_used=tools_used,
        )

    def _live_chat(self, messages: list[dict[str, str]]) -> str:
        if OpenAI is None:
            return "[error] 未安装 openai 包"
        if self._client is None:
            self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content or ""
