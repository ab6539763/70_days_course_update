# -*- coding: utf-8 -*-
"""Day 57 验收脚本 —— SPARKTECH_MOCK=1 无需 GPU / API Key / Docker。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))
os.environ.setdefault("SPARKTECH_MOCK", "1")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def main() -> None:
    print("=== Day 57 verify ===")

    from deploy_stack.api_gateway.main import health
    from deploy_stack.mock_vllm_app import health as vllm_health
    from deploy_stack.api_gateway import main as gw
    from fastapi.testclient import TestClient

    if health().get("status") != "ok":
        fail("gateway health")
    ok("gateway health")

    if vllm_health().get("status") != "ok":
        fail("vllm health")
    ok("mock vllm health")

    client = TestClient(gw.app)
    r = client.post("/api/chat", json={"message": "退款", "route": "finetuned"})
    if r.status_code != 200 or "reply" not in r.json():
        fail("finetuned chat")
    ok("gateway /api/chat")

    r2 = client.post("/api/chat", json={"message": "政策", "route": "rag"})
    if "RAG" not in r2.json().get("reply", ""):
        fail("rag route")
    ok("rag route")

    compose = CODE_DIR / "deploy_stack" / "docker-compose.yml"
    if not compose.is_file():
        fail("docker-compose missing")
    ok("docker-compose.yml")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
