# -*- coding: utf-8 -*-
"""Day 21 验收脚本 —— 无 API Key 时全部 mock 通过。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

# 强制 mock，避免 CI 无 Key 失败
os.environ.setdefault("SPARKTECH_MOCK", "1")

from integrated_assistant import (  # noqa: E402
    ConversationSession,
    IntegratedAssistant,
    IntegratedClient,
    ToolRegistry,
    stream_tokens,
)


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_session() -> None:
    s = ConversationSession()
    s.add_user_message("你好")
    s.add_assistant_message("你好！")
    msgs = s.to_api_messages()
    assert msgs[0]["role"] == "system"
    assert any(m["role"] == "user" for m in msgs)
    s.clear()
    assert s.message_count == 1
    ok("ConversationSession add/clear")


def test_trim() -> None:
    s = ConversationSession()
    for i in range(25):
        s.add_user_message(f"msg-{i}")
    s.trim(max_messages=5)
    non_system = [m for m in s.to_api_messages() if m["role"] != "system"]
    assert len(non_system) <= 5
    ok("ConversationSession trim")


def test_tools() -> None:
    reg = ToolRegistry()
    names = reg.list_tools()
    assert "get_weather" in names
    assert "lookup_order" in names
    assert "calc" in names

    weather = reg.maybe_invoke("北京天气怎么样")
    assert weather is not None and weather.name == "get_weather"
    result = reg.execute(weather.name, weather.arguments)
    assert "北京" in result

    order = reg.maybe_invoke("查订单 ST-10086")
    assert order is not None and order.name == "lookup_order"

    calc = reg.maybe_invoke("计算 2+3")
    assert calc is not None and calc.name == "calc"
    calc_result = reg.execute(calc.name, calc.arguments)
    assert "5" in calc_result

    ok("ToolRegistry weather/order/calc")


def test_stream() -> None:
    chunks = list(stream_tokens("hello", chunk_size=2))
    assert "".join(chunks) == "hello"
    assert len(chunks) >= 1
    ok("stream_tokens")


def test_mock_chat() -> None:
    client = IntegratedClient()
    assert client.is_mock_mode
    result = client.chat(
        [
            {"role": "system", "content": "test"},
            {"role": "user", "content": "ping"},
        ]
    )
    assert result.text
    assert result.mock
    ok("IntegratedClient mock chat")


def test_assistant_round() -> None:
    assistant = IntegratedAssistant()
    assistant.stream_enabled = False
    reply = assistant.handle_user_input("上海天气")
    assert reply
    assert assistant.session.message_count >= 3
    ok("IntegratedAssistant weather round")


def main() -> None:
    print("=== Day 21 verify ===\n")
    test_session()
    test_trim()
    test_tools()
    test_stream()
    test_mock_chat()
    test_assistant_round()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
