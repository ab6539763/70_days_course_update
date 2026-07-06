# -*- coding: utf-8 -*-
"""Project 2 验收脚本 —— 文档摄取、问答、流式、引用。"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

_TEST_DIR = tempfile.mkdtemp(prefix="project2_verify_")
os.environ["SQLITE_PATH"] = str(Path(_TEST_DIR) / "kb_qa.db")
os.environ["SPARKTECH_MOCK"] = "1"

from fastapi.testclient import TestClient  # noqa: E402

from backend.database import SessionLocal, init_db  # noqa: E402
from backend.document_ingest import ingest_bytes  # noqa: E402
from backend.main import app  # noqa: E402
from backend.models import DocumentRecord, KnowledgeChunk  # noqa: E402
from backend.rag_service import get_rag_service  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_ingest_txt_md() -> None:
    init_db()
    db = SessionLocal()
    try:
        txt = "退款可在7天内申请无理由退款。".encode("utf-8")
        md = "# SLA\nP0 故障 15 分钟响应。".encode("utf-8")
        r1 = ingest_bytes(db, "refund.txt", txt)
        r2 = ingest_bytes(db, "sla.md", md)
        assert r1.document.chunk_count >= 1
        assert r2.document.chunk_count >= 1
        total = db.query(KnowledgeChunk).count()
        assert total >= 2
    finally:
        db.close()
    ok(f"ingest txt/md ({total} chunks)")


def test_hybrid_retrieve_citations() -> None:
    db = SessionLocal()
    try:
        rag = get_rag_service()
        rag.load_index(db)
        cites = rag.retrieve(db, "退款 7 天", top_k=3)
        assert cites, "应有引用结果"
        assert any("refund" in c.source.lower() or "退款" in c.snippet for c in cites)
    finally:
        db.close()
    ok("hybrid retrieve + citations")


def test_ask_non_stream() -> None:
    sid = "verify-ask"
    with TestClient(app) as client:
        res = client.post(
            "/api/chat",
            json={"message": "如何申请退款？", "session_id": sid, "stream": False},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["reply"]
        assert data["mode"] == "mock"
        assert data["citations"], "应答含 citations"
        assert any("退款" in c["snippet"] or "refund" in c["source"].lower() for c in data["citations"])
    ok("POST /api/chat with citations")


def _parse_sse_events(raw: str) -> list[dict]:
    events: list[dict] = []
    for block in raw.split("\n\n"):
        for line in block.split("\n"):
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))
    return events


def test_sse_stream_citations() -> None:
    sid = "verify-stream"
    with TestClient(app) as client:
        with client.stream(
            "POST",
            "/api/chat/stream",
            json={"message": "API Key 怎么申请？", "session_id": sid, "stream": True},
        ) as res:
            assert res.status_code == 200
            assert "text/event-stream" in res.headers.get("content-type", "")
            body = res.read().decode()

        events = _parse_sse_events(body)
        cite_events = [e for e in events if e.get("event") == "citations"]
        deltas = [e["delta"] for e in events if e.get("event") == "delta"]
        done = [e for e in events if e.get("event") == "done"]
        assert cite_events, "应有 citations 事件"
        assert cite_events[0].get("citations"), "citations 非空"
        assert deltas, "应有 delta 事件"
        assert done, "应有 done 事件"
        full = "".join(deltas)
        assert full

        hist = client.get(f"/api/sessions/{sid}/history")
        msgs = hist.json()["messages"]
        assistant = [m for m in msgs if m["role"] == "assistant"]
        assert assistant and assistant[-1]["citations"]
    ok("POST /api/chat/stream SSE + citations persist")


def test_upload_api() -> None:
    with TestClient(app) as client:
        content = "# Upload Test\n企业版按年订阅 12 万起。".encode("utf-8")
        res = client.post(
            "/api/documents/upload",
            files=[("files", ("upload_test.md", content, "text/markdown"))],
        )
        assert res.status_code == 200
        data = res.json()
        assert data["uploaded"]
        assert data["rebuilt_chunks"] >= 1

        docs = client.get("/api/documents")
        assert docs.json()["total"] >= 1
    ok("POST /api/documents/upload")


def test_health() -> None:
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["mode"] == "mock"
        assert data["chunk_count"] >= 1
    ok("GET /health")


def test_rebuild_index() -> None:
    with TestClient(app) as client:
        res = client.post("/api/kb/rebuild")
        assert res.status_code == 200
        data = res.json()
        assert data["chunk_count"] >= 1
    ok("POST /api/kb/rebuild")


def main() -> None:
    print("=== Project 2 verify ===\n")
    test_ingest_txt_md()
    test_hybrid_retrieve_citations()
    test_health()
    test_ask_non_stream()
    test_sse_stream_citations()
    test_upload_api()
    test_rebuild_index()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
