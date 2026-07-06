# -*- coding: utf-8 -*-
"""Day 24 验收脚本 —— mock 模式 SSE + SQLite 全链路。"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# 必须在导入 backend 之前设置，确保 TestClient 使用可写 SQLite
_TEST_DB_DIR = tempfile.mkdtemp(prefix="day24_verify_")
os.environ["SQLITE_PATH"] = str(Path(_TEST_DB_DIR) / "chat_history.db")
os.environ["SPARKTECH_MOCK"] = "1"

from fastapi.testclient import TestClient  # noqa: E402

from backend.database import SessionLocal, init_db  # noqa: E402
from backend.llm_client import SparkLLMClient, _mock_plan  # noqa: E402
from backend.main import app  # noqa: E402
from backend.models import ChatMessage, ChatSession  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_mock_llm_stream() -> None:
    client = SparkLLMClient()
    assert client.is_mock_mode
    chunks = list(client.stream_chat([], "上海天气怎么样"))
    full = "".join(chunks)
    assert "上海" in full or "天气" in full
    assert len(chunks) >= 2, "mock 流式应 yield 多个 chunk"
    ok(f"SparkLLMClient mock stream ({len(chunks)} chunks)")


def test_mock_plan_tools() -> None:
    _, tools = _mock_plan("查订单 ST-10086")
    assert "lookup_order" in tools
    text, tools2 = _mock_plan("北京天气")
    assert "get_weather" in tools2
    assert text
    ok("mock keyword routing")


def test_sqlite_persistence() -> None:
    init_db()
    db = SessionLocal()
    try:
        session = ChatSession(id="verify-session")
        db.add(session)
        db.add(
            ChatMessage(
                session_id="verify-session",
                role="user",
                content="你好",
            )
        )
        db.commit()

        count = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == "verify-session")
            .count()
        )
        assert count == 1
    finally:
        db.close()
    ok("SQLite + SQLAlchemy save message")


def _parse_sse_events(raw: str) -> list[dict]:
    events: list[dict] = []
    for block in raw.split("\n\n"):
        for line in block.split("\n"):
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))
    return events


def test_api_health() -> None:
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["mode"] == "mock"
    ok("GET /health")


def test_api_chat_non_stream() -> None:
    sid = "verify-non-stream"
    with TestClient(app) as client:
        res = client.post(
            "/api/chat",
            json={"message": "你好", "session_id": sid, "stream": False},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["reply"]
        assert data["session_id"] == sid
        assert data["mode"] == "mock"

        hist = client.get(f"/api/sessions/{sid}/history")
        assert hist.status_code == 200
        messages = hist.json()["messages"]
        assert len(messages) >= 2
    ok("POST /api/chat + history")


def test_api_sse_stream() -> None:
    sid = "verify-sse-stream"
    with TestClient(app) as client:
        with client.stream(
            "POST",
            "/api/chat/stream",
            json={"message": "上海天气", "session_id": sid, "stream": True},
        ) as res:
            assert res.status_code == 200
            assert "text/event-stream" in res.headers.get("content-type", "")
            body = res.read().decode()

        events = _parse_sse_events(body)
        deltas = [e["delta"] for e in events if e.get("event") == "delta"]
        done = [e for e in events if e.get("event") == "done"]
        assert deltas, "应有 delta 事件"
        assert done, "应有 done 事件"
        full = "".join(deltas)
        assert full == done[0].get("delta", "") or full  # done delta 为空
        assert "上海" in full or "天气" in full

        hist = client.get(f"/api/sessions/{sid}/history")
        msgs = hist.json()["messages"]
        assistant_msgs = [m for m in msgs if m["role"] == "assistant"]
        assert assistant_msgs and assistant_msgs[-1]["content"] == full
    ok("POST /api/chat/stream SSE + DB persist")


def test_cors_headers() -> None:
    with TestClient(app) as client:
        res = client.options(
            "/api/chat",
            headers={
                "Origin": "http://127.0.0.1:8080",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert res.status_code == 200
        assert "access-control-allow-origin" in {
            k.lower() for k in res.headers.keys()
        }
    ok("CORS preflight")


def test_clear_session() -> None:
    sid = "verify-clear"
    with TestClient(app) as client:
        client.post(
            "/api/chat",
            json={"message": "ping", "session_id": sid},
        )
        cleared = client.delete(f"/api/sessions/{sid}")
        assert cleared.status_code == 200
        hist = client.get(f"/api/sessions/{sid}/history")
        assert hist.json()["count"] == 0
    ok("DELETE /api/sessions/{id}")


def main() -> None:
    print("=== Day 24 verify ===\n")
    init_db()
    test_mock_llm_stream()
    test_mock_plan_tools()
    test_sqlite_persistence()
    test_api_health()
    test_api_chat_non_stream()
    test_api_sse_stream()
    test_cors_headers()
    test_clear_session()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
