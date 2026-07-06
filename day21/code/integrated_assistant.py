# -*- coding: utf-8 -*-
"""
Day 21 · Week 3 综合助手

整合 Day 15–20 能力：
- 多轮对话（ConversationSession）
- 工具调用（ToolRegistry + mock 关键词路由）
- 流式输出（stream_tokens / stream_chat）

运行：
  cd day21/code && python3 integrated_assistant.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Generator, Iterator

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[misc, assignment]


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

CODE_DIR = Path(__file__).resolve().parent
MAX_TOOL_ROUNDS = 3
DEFAULT_MAX_MESSAGES = 20

SYSTEM_PROMPT = """你是星火智服（SparkTech）智能客服助手。
你可以使用以下工具帮助用户：
- get_weather：查询城市天气（用户提到天气、气温时）
- lookup_order：查询订单状态（用户提到订单号 ST-xxxxx 时）
- calc：数学计算（用户提到计算、加减乘除时）

回答简洁友好，使用中文。若已调用工具，请基于工具结果组织自然语言回复。"""


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


# ---------------------------------------------------------------------------
# 会话
# ---------------------------------------------------------------------------


class ConversationSession:
    """多轮对话会话，维护 OpenAI 格式 messages 列表。"""

    def __init__(self, *, system_prompt: str = SYSTEM_PROMPT) -> None:
        self._messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    @property
    def message_count(self) -> int:
        return len(self._messages)

    def add_user_message(self, text: str) -> None:
        text = text.strip()
        if not text:
            raise ValueError("用户消息不能为空")
        self._messages.append({"role": "user", "content": text})
        self._auto_trim()

    def add_assistant_message(self, text: str) -> None:
        self._messages.append({"role": "assistant", "content": text})
        self._auto_trim()

    def add_tool_result(self, tool_name: str, result: str) -> None:
        """教学简化：用 user 前缀标记工具结果，便于终端阅读。"""
        self._messages.append(
            {
                "role": "user",
                "content": f"[tool_result:{tool_name}] {result}",
            }
        )
        self._auto_trim()

    def to_api_messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    def clear(self) -> None:
        system = [m for m in self._messages if m["role"] == "system"]
        self._messages = system or [{"role": "system", "content": SYSTEM_PROMPT}]

    def trim(self, max_messages: int = DEFAULT_MAX_MESSAGES) -> None:
        system = [m for m in self._messages if m["role"] == "system"]
        rest = [m for m in self._messages if m["role"] != "system"]
        self._messages = system + rest[-max_messages:]

    def recent_summary(self, n: int = 5) -> str:
        lines: list[str] = []
        for msg in self._messages[-n:]:
            role = msg["role"]
            content = msg["content"]
            preview = content[:60] + ("…" if len(content) > 60 else "")
            lines.append(f"  [{role}] {preview}")
        return "\n".join(lines) if lines else "  （空）"

    def _auto_trim(self) -> None:
        non_system = sum(1 for m in self._messages if m["role"] != "system")
        if non_system > DEFAULT_MAX_MESSAGES:
            self.trim(DEFAULT_MAX_MESSAGES)


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------


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


# mock 订单库
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


def _handle_get_weather(args: dict[str, Any]) -> str:
    city = str(args.get("city", "北京"))
    # 确定性 mock：按城市名哈希
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
    # 安全：仅允许数字与四则运算
    if not re.fullmatch(r"[\d\s+\-*/().]+", expr):
        return json.dumps({"error": "表达式含非法字符", "expression": expr})
    try:
        value = eval(expr, {"__builtins__": {}}, {})  # noqa: S307 教学 mock
        return json.dumps({"expression": expr, "result": value}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc), "expression": expr})


def _extract_city(text: str) -> str:
    for marker in ("天气", "气温", "温度"):
        if marker in text:
            idx = text.index(marker)
            prefix = text[:idx].strip()
            # 取 marker 前 2–6 字作为城市名
            city = re.sub(r"[查的一下怎样如何]*", "", prefix)
            city = city.strip() or "北京"
            return city[-6:] if len(city) > 6 else city
    return "北京"


def _extract_order_id(text: str) -> str:
    match = re.search(r"ST-?\d+", text, re.IGNORECASE)
    if match:
        raw = match.group(0).upper()
        return raw if raw.startswith("ST-") else f"ST-{raw[2:]}"
    return "ST-10086"


def _extract_expression(text: str) -> str:
    # 去掉中文触发词
    expr = re.sub(r"(计算|等于|请算|帮我算)", "", text)
    expr = expr.strip()
    # 全角运算符转半角
    expr = expr.replace("×", "*").replace("÷", "/")
    return expr or "0"


class ToolRegistry:
    """工具注册表：mock 关键词路由 + OpenAI schema 导出。"""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(
            ToolSpec(
                name="get_weather",
                description="查询指定城市的当前天气",
                parameters={
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
                handler=_handle_get_weather,
                keywords=("天气", "气温", "温度", "下雨"),
            )
        )
        self.register(
            ToolSpec(
                name="lookup_order",
                description="根据订单号查询物流状态",
                parameters={
                    "type": "object",
                    "properties": {"order_id": {"type": "string"}},
                    "required": ["order_id"],
                },
                handler=_handle_lookup_order,
                keywords=("订单", "物流", "ST-", "st-"),
            )
        )
        self.register(
            ToolSpec(
                name="calc",
                description="计算数学表达式",
                parameters={
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"],
                },
                handler=_handle_calc,
                keywords=("计算", "等于", "乘", "除", "加", "减"),
            )
        )

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def to_openai_schemas(self) -> list[dict[str, Any]]:
        schemas: list[dict[str, Any]] = []
        for spec in self._tools.values():
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": spec.name,
                        "description": spec.description,
                        "parameters": spec.parameters,
                    },
                }
            )
        return schemas

    def maybe_invoke(self, user_text: str) -> ToolCall | None:
        """mock 模式：关键词匹配决定调用哪个工具。"""
        text = user_text.strip()
        if not text:
            return None

        # 订单号优先（避免 ST-10086 中的 '-' 误触计算工具）
        if re.search(r"ST-?\d+", text, re.IGNORECASE) or "订单" in text:
            return ToolCall(
                name="lookup_order",
                arguments=self._build_args(self._tools["lookup_order"], text),
            )

        # 算术表达式：含数字与运算符
        if re.search(r"\d\s*[\+\-\*/]\s*\d", text) or any(
            kw in text for kw in ("计算", "等于", "乘", "除", "加", "减")
        ):
            return ToolCall(
                name="calc",
                arguments=self._build_args(self._tools["calc"], text),
            )

        for name in self.list_tools():
            if name in ("lookup_order", "calc"):
                continue
            spec = self._tools[name]
            if any(kw in text for kw in spec.keywords):
                return ToolCall(name=name, arguments=self._build_args(spec, text))
        return None

    def _build_args(self, spec: ToolSpec, text: str) -> dict[str, Any]:
        if spec.name == "get_weather":
            return {"city": _extract_city(text)}
        if spec.name == "lookup_order":
            return {"order_id": _extract_order_id(text)}
        if spec.name == "calc":
            return {"expression": _extract_expression(text)}
        return {}

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        spec = self._tools.get(name)
        if spec is None:
            return json.dumps({"error": f"未知工具: {name}"})
        return spec.handler(arguments)


# ---------------------------------------------------------------------------
# 流式
# ---------------------------------------------------------------------------


def stream_tokens(text: str, *, chunk_size: int = 2) -> Generator[str, None, None]:
    """按 chunk_size 字符 yield，模拟 Day 20 SSE token 流。"""
    if not text:
        return
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]
        time.sleep(0.02)  # 教学可见性


# ---------------------------------------------------------------------------
# LLM 客户端
# ---------------------------------------------------------------------------


@dataclass
class ChatResult:
    text: str
    mock: bool = True
    model: str = "gpt-4o-mini"


class IntegratedClient:
    """mock 优先；配置 Key 且 SPARKTECH_MOCK=0 时走 live API。"""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.7,
    ) -> None:
        _load_env()
        self._api_key = api_key if api_key is not None else get_env("OPENAI_API_KEY")
        self._model = model or get_env("OPENAI_MODEL", "gpt-4o-mini")
        self._base_url = base_url or get_env(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        )
        self._temperature = temperature
        mock_flag = get_env("SPARKTECH_MOCK", "1")
        self._force_mock = mock_flag in ("1", "true", "yes", "")
        self._client: Any | None = None
        self._turn = 0

    @property
    def is_mock_mode(self) -> bool:
        return self._force_mock or not self._api_key

    def chat(self, messages: list[dict[str, str]]) -> ChatResult:
        self._turn += 1
        if self.is_mock_mode:
            return ChatResult(text=self._mock_reply(messages), mock=True, model=self._model)
        return self._live_chat(messages)

    def stream_chat(self, messages: list[dict[str, str]]) -> Iterator[str]:
        result = self.chat(messages)
        yield from stream_tokens(result.text)

    def _mock_reply(self, messages: list[dict[str, str]]) -> str:
        last_user = ""
        tool_context = ""
        for msg in reversed(messages):
            if msg["role"] == "user" and not msg["content"].startswith("[tool_result:"):
                last_user = msg["content"]
                break
        for msg in reversed(messages):
            if msg["content"].startswith("[tool_result:"):
                tool_context = msg["content"]
                break

        if tool_context:
            return self._format_tool_reply(tool_context)

        name_hint = ""
        for msg in messages:
            if msg["role"] == "user" and "我叫" in msg["content"]:
                name_hint = msg["content"]
        if "叫什么" in last_user or "我的名字" in last_user:
            for msg in messages:
                if msg["role"] == "user" and "我叫" in msg["content"]:
                    m = re.search(r"我叫(\S+)", msg["content"])
                    if m:
                        return f"你叫{m.group(1)}。"

        return (
            f"[mock/{self._model}] 已收到：「{_preview(last_user)}」。"
            f"（第 {self._turn} 轮，上下文 {len(messages)} 条）"
            f"{' 提示：可问天气、订单 ST-10086、或计算式。' if self._turn == 1 else ''}"
        )

    def _format_tool_reply(self, tool_context: str) -> str:
        if "get_weather" in tool_context:
            try:
                raw = tool_context.split("]", 1)[1].strip()
                data = json.loads(raw)
                return (
                    f"{data['city']}当前天气：{data['condition']}，"
                    f"{data['temp_c']}°C，湿度 {data['humidity_pct']}%。"
                    f"（数据来源：{data.get('source', 'mock')}）"
                )
            except (json.JSONDecodeError, KeyError):
                pass
        if "lookup_order" in tool_context:
            try:
                raw = tool_context.split("]", 1)[1].strip()
                data = json.loads(raw)
                return (
                    f"订单 {data['order_id']}：{data['status']}，"
                    f"承运 {data.get('carrier', '-')}，"
                    f"预计 {data.get('eta', '-')} 送达。"
                )
            except (json.JSONDecodeError, KeyError):
                pass
        if "calc" in tool_context:
            try:
                raw = tool_context.split("]", 1)[1].strip()
                data = json.loads(raw)
                if "error" in data:
                    return f"计算失败：{data['error']}"
                return f"{data['expression']} = {data['result']}"
            except (json.JSONDecodeError, KeyError):
                pass
        return f"已处理工具结果：{_preview(tool_context, 80)}"

    def _live_chat(self, messages: list[dict[str, str]]) -> ChatResult:
        if OpenAI is None:
            return ChatResult(
                text="[error] 未安装 openai 包，请 pip install -r requirements.txt",
                mock=True,
            )
        if self._client is None:
            self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
        )
        text = response.choices[0].message.content or ""
        return ChatResult(text=text, mock=False, model=self._model)

    def describe(self) -> str:
        mode = "mock" if self.is_mock_mode else "live"
        return f"IntegratedClient(model={self._model}, mode={mode})"


def _preview(text: str, max_len: int = 40) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


# ---------------------------------------------------------------------------
# 综合助手
# ---------------------------------------------------------------------------


HELP_TEXT = """
命令：
  /help              显示帮助
  /clear             清空对话历史
  /tools             列出已注册工具
  /stream on|off     开关流式输出
  /history           最近 5 条消息摘要
  /exit              退出

直接输入文字开始对话。支持：天气查询、订单 ST-xxxxx、数学计算。
""".strip()

BANNER = """
╔══════════════════════════════════════════════════════════╗
║  星火智服 · Day 21 Week 3 综合助手                        ║
║  多轮对话 + 工具调用 + 流式输出                           ║
╚══════════════════════════════════════════════════════════╝
""".strip()


class IntegratedAssistant:
    """编排 session、tools、client 的综合助手。"""

    def __init__(self) -> None:
        self.session = ConversationSession()
        self.tools = ToolRegistry()
        self.client = IntegratedClient()
        stream_default = get_env("STREAM_DEFAULT", "on").lower()
        self.stream_enabled = stream_default in ("on", "1", "true", "yes")

    def handle_user_input(self, user_text: str) -> str:
        """处理一轮用户输入，返回完整 assistant 文本（流式时仍返回拼接结果）。"""
        self.session.add_user_message(user_text)

        # Agent 工具环（mock：每轮用户输入最多执行一次工具）
        for _ in range(MAX_TOOL_ROUNDS):
            tool_call = self.tools.maybe_invoke(user_text)
            if tool_call is None:
                break
            result = self.tools.execute(tool_call.name, tool_call.arguments)
            self.session.add_tool_result(tool_call.name, result)
            # mock 模式一轮用户输入只触发一次工具
            break

        messages = self.session.to_api_messages()
        if self.stream_enabled:
            print("\n助手> ", end="", flush=True)
            full = ""
            for chunk in self.client.stream_chat(messages):
                print(chunk, end="", flush=True)
                full += chunk
            print("\n")
            self.session.add_assistant_message(full)
            return full

        result = self.client.chat(messages)
        prefix = "" if not result.mock else ""
        reply = f"{prefix}{result.text}"
        print(f"\n助手> {reply}\n")
        self.session.add_assistant_message(reply)
        return reply

    def handle_command(self, line: str) -> tuple[str, bool]:
        """处理斜杠命令。返回 (输出, should_exit)。"""
        parts = line.strip().split()
        cmd = parts[0].lower()

        if cmd == "/help":
            return HELP_TEXT, False
        if cmd == "/clear":
            self.session.clear()
            return "会话已清空。", False
        if cmd == "/tools":
            names = ", ".join(self.tools.list_tools())
            return f"已注册工具：{names}", False
        if cmd == "/history":
            return "最近消息：\n" + self.session.recent_summary(5), False
        if cmd == "/stream":
            if len(parts) < 2 or parts[1] not in ("on", "off"):
                return "用法：/stream on 或 /stream off", False
            self.stream_enabled = parts[1] == "on"
            state = "开启" if self.stream_enabled else "关闭"
            return f"流式输出已{state}。", False
        if cmd in ("/exit", "/quit"):
            return "再见！", True
        return f"未知命令：{cmd}。输入 /help 查看帮助。", False

    def run_repl(self) -> int:
        print(BANNER)
        print(self.client.describe())
        print(f"流式输出：{'on' if self.stream_enabled else 'off'}")
        print("输入 /help 查看命令。\n")

        while True:
            try:
                user_input = input("你> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n已中断，输入 /exit 可正常退出。")
                continue

            if not user_input:
                continue

            if user_input.startswith("/"):
                message, should_exit = self.handle_command(user_input)
                print(message)
                if should_exit:
                    return 0
                continue

            try:
                self.handle_user_input(user_input)
            except ValueError as exc:
                print(f"[输入错误] {exc}")
            except Exception as exc:
                print(f"[错误] {exc}")

        return 0


def main() -> None:
    raise SystemExit(IntegratedAssistant().run_repl())


if __name__ == "__main__":
    main()
