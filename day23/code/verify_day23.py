# -*- coding: utf-8 -*-
"""Day 23 验收脚本 —— 无 API Key 时全部 mock 通过。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ.setdefault("SPARKTECH_MOCK", "1")

from chat_service import ChatService, ToolRegistry  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402
from models import ChatRequest  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_pydantic_validation() -> None:
    try:
        ChatRequest(message="   ")
        fail("空白 message 应校验失败")
    except ValueError:
        pass

    req = ChatRequest(message="  hello  ", session_id="s1")
    assert req.message == "hello"
    ok("ChatRequest strip + validation")


def test_tools() -> None:
    reg = ToolRegistry()
    weather = reg.maybe_invoke("北京天气怎么样")
    assert weather is not None and weather.name == "get_weather"
    result = reg.execute(weather.name, weather.arguments)
    assert "北京" in result

    order = reg.maybe_invoke("查订单 ST-10086")
    assert order is not None and order.name == "lookup_order"

    calc = reg.maybe_invoke("计算 2+3")
    assert calc is not None and calc.name == "calc"
    ok("ToolRegistry weather/order/calc")


def test_chat_service_mock() -> None:
    svc = ChatService()
    assert svc.is_mock_mode

    weather = svc.chat(
        ChatRequest(message="上海天气", session_id="verify-weather")
    )
    assert "天气" in weather.reply
    assert weather.tools_used == ["get_weather"]

    order = svc.chat(
        ChatRequest(message="订单 ST-10086", session_id="verify-order")
    )
    assert "ST-10086" in order.reply
    assert "lookup_order" in order.tools_used

    hello = svc.chat(
        ChatRequest(message="你好", session_id="verify-hello")
    )
    assert "您好" in hello.reply
    ok("ChatService mock weather/order/hello")


def test_fastapi_routes() -> None:
    client = TestClient(app)

    root = client.get("/")
    assert root.status_code == 200
    assert "星火智服" in root.json()["service"]

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["mode"] == "mock"

    item = client.get("/items/7", params={"q": "spark"})
    assert item.status_code == 200
    assert item.json() == {"item_id": 7, "q": "spark"}

    ok("FastAPI root/health/path+query params")


def test_api_chat_contract() -> None:
    client = TestClient(app)
    payload = {
        "message": "查上海天气",
        "session_id": "web-demo-001",
        "stream": False,
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "reply" in data
    assert data["session_id"] == "web-demo-001"
    assert isinstance(data["tools_used"], list)
    assert "get_weather" in data["tools_used"]
    ok("POST /api/chat Day22 contract")


def test_stream_not_implemented() -> None:
    client = TestClient(app)
    res = client.post(
        "/api/chat",
        json={"message": "hi", "session_id": "s", "stream": True},
    )
    assert res.status_code == 501
    ok("stream=true returns 501 on Day23")


def main() -> None:
    print("=== Day 23 verify ===\n")
    test_pydantic_validation()
    test_tools()
    test_chat_service_mock()
    test_fastapi_routes()
    test_api_chat_contract()
    test_stream_not_implemented()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
